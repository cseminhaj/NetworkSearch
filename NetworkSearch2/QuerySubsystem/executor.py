""" a executor class for an aggregator execution.

It defines an executor class used for an execution of
an aggregator in Echo protocol. In the executor class,
it has two method exposes to other modules, i.e., execute()
and aggregate(). The methods here are delegated from the Echo aggregator.

Author: Thanakorn Sueverachai, Misbah Uddin
Last updated: 30 March 2014
"""

import logging
import pymongo
from math import sqrt
import operator
import itertools
import urllib
import json
# for profiling
from NetworkSearch2.ProfileTools.myProfiler import Profiler
from datetime import datetime
from time import time

class executor:
    """ a class defines the execution of the aggragator for the echo protocol. """
    
    def __init__(self):
        self.mongo_connection = pymongo.MongoClient("127.0.0.1",27017)
    
    def _compute_rank_weights(self,query):

        ks = float(query.parameters['weightScore']['ks'])
        ds = float(query.parameters['weightScore']['ds'])
        fs = float(query.parameters['weightScore']['fs'])
        
        if query.parameters['isVicinity']==True:
           kw = float(ks/(ks+ds+fs))
           dw = float(ds/(ks+ds+fs))
           fw = float(fs/(ks+ds+fs))
        else:
           kw = float(ks/(ks+fs))
           fw = float(fs/(ks+fs))
           dw = 0

        return {'kw':kw,'dw':dw,'fw':fw}


    def _compute_distance_google_map(self,poi,obj):
         url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={'+poi+'}&destinations={'+obj+'}&mode=walking&language=en-EN&sensor=false'
         distance_matrix = json.load(urllib.urlopen(url))
         distance_number = int(distance_matrix['rows'][0]['elements'][0]['duration']['value'])
         distance_text = distance_matrix['rows'][0]['elements'][0]['duration']['text']
         return distance_number, distance_text

    def _compute_distance_score(self,location_type,distance,distance_threshold):
        
		if location_type=='network':
			return 0
		elif location_type=='geographic':
			if distance < distance_threshold:
				if distance == 0: 
					return 1
				else:
					return 1/float(distance)
			else:
				return 1/float(distance)*1/float(distance-distance_threshold)
     
    def _compute_ranking_score(self,query,objects,node_distance):
        if query.parameters['isVicinity']==True:
            distance_threshold = int(query.parameters['vicinity']['distance-measure'])*60
        poi=query.parameters['vicinity']['location']                                                                                   
        time_ref = datetime(2014,03,17,8,0,0,0)
        current_time = datetime.now()
        rank_weights = self._compute_rank_weights(query) 
	
        for oid,obj in objects.items():
            object_time = obj['timestamp']
            object_location = obj['object-location']
            location_type = obj['location-type']
            keyword_score = obj['total_score']
            freshness_score = (object_time - time_ref).total_seconds()/(current_time-time_ref).total_seconds()
            if query.parameters['isVicinity']==True:
                num_rank_signals = 3 
                if query.parameters['vicinity-precision']==True and location_type=='geographic':
                    distance, distText = self._compute_distance_google_map(poi,object_location)
                    obj['distance'] = distText
                    distance_score = self._compute_distance_score(location_type,distance,distance_threshold)
                elif query.parameters['vicinity-precision']==False and location_type=='geographic':
                    distance_score = self._compute_distance_score(location_type,int(node_distance),distance_threshold)            
                elif location_type=='network':
                    distance_score = self._compute_distance_score(location_type,0,0)
            else:
                distance_score = 0
                num_rank_signals = 2
            total_score = (rank_weights['kw']*keyword_score + rank_weights['fw']*freshness_score + rank_weights['dw']*distance_score)/num_rank_signals
            obj['total_score']=total_score   
        return objects

    def _match(self,query):

        collection = self.mongo_connection["index"]["termdoc"] 
        with Profiler("index_DB_access_for_approx_match"):
            results = list(collection.find(query.match_statement))
        return results
        
    @Profiler.profile('Ranking')    
    def _compute_matching_score(self,query,results_cursor):
        
        num_keywords = float(len(query.match_statement['$or']))
        
        results = {}
        list_results =[]
        for new_obj in results_cursor:
            if results.has_key(new_obj['document']):
                result_object = results[new_obj['document']]
                result_object['tf_score'] = result_object['tf_score'] + new_obj['tf']**2 if new_obj.has_key('tf') else result_object['tf_score']
                result_object['nr_score'] = result_object['nr_score'] + new_obj['nr'] if new_obj.has_key('nr') else result_object['nr_score']
                result_object['tr_score'] = result_object['tr_score'] + new_obj['tr'] if new_obj.has_key('tr') else result_object['tr_score']
                
            else:
                new_obj['tf_score'] = new_obj['tf']**2 if new_obj.has_key('tf') else 0
                new_obj['nr_score'] = new_obj['nr'] if new_obj.has_key('nr') else 0
                new_obj['tr_score'] = new_obj['tr'] if new_obj.has_key('tr') else 0
                results[new_obj['document']] = new_obj
        for result in results.itervalues():
           tf_score = query.parameters['weightScore']['tf'] * result['tf_score']/num_keywords 
           nr_score = query.parameters['weightScore']['nr'] * result['nr_score']/num_keywords
           tr_score = query.parameters['weightScore']['tr'] * result['tr_score']/num_keywords
           total_weight = query.parameters['weightScore']['tf']+query.parameters['weightScore']['nr']+query.parameters['weightScore']['tr']
           result['total_score'] = (tf_score + nr_score + tr_score)/total_weight
           list_results.append(result)
        
        return list_results
    
    @Profiler.profile('Aggregator.local()')
    def execute(self,query,node_distance):
        
        object_collection = self.mongo_connection["sensor"]["objects"]
        limit = query.parameters['limit']
        if query.parameters['isApprox']==True:
            results = self._match(query)
            results = self._compute_matching_score(query,results)
            sorted_results = sorted(results, key=operator.itemgetter('total_score'),reverse=True)
            sorted_results = sorted_results[:limit]
            
            # get list of real-object oids from the index
            oid_list = map(operator.itemgetter('document'),sorted_results)
            with Profiler("object_DB_access_for_approx_match"):
                # get actual objects
                if oid_list:
                    real_object_results = list(object_collection.find({"_id":{'$in':oid_list}},{"content":0})) 
                else:
                    return []

            # add 'total_score' attribute to the real object
            temp = {}
			
            for obj in real_object_results:
                temp[obj['_id']] = obj
            
            for obj_index in sorted_results:
                try:
                    temp[obj_index['document']]['total_score'] = obj_index['total_score']
                except KeyError:
                    logging.warning("mismatch index object and real object : " + str(obj_index['document']))

            temp = self._compute_ranking_score(query,temp,node_distance)
            results = temp.itervalues()
            return sorted(results, key=operator.itemgetter('total_score'),reverse=True)

        else:
            temp = self._match(query)
            num_keywords = float(len(query.match_statement['$or']))
            temp_results = {}
            oids = []
            for obj in temp:
                if temp_results.has_key(obj['document']):
                    tmp = temp_results[obj['document']]['tf_score']
                    temp_results[obj['document']]['tf_score']=tmp + 1
                else:
                    temp_results[obj['document']]=obj
                    temp_results[obj['document']]['tf_score']=1
            for key in temp_results.iterkeys():
                tmp = temp_results[key]['tf_score']
                temp_results[key]['tf_score'] = float(tmp) / num_keywords
                if temp_results[key]['tf_score']==1.0:
			       oids.append(key)
            if len(oids)>0:
                real_object_results = list(object_collection.find({"_id":{'$in':oids}},{"content":0}))
                return real_object_results
            else:
                return []

    @Profiler.profile('Aggregator.aggregate()')
    def aggregate(self,local_result,agg,limit,aggregation_function_list):
        """ (QueryObject) -> list of json object
        execute the aggregate function of an aggregator . (similar to A.aggregate() in echo context
        """
        temp = local_result[:]
        temp.extend(agg)
        return sorted(temp, key=operator.itemgetter('total_score'),reverse=True)[:limit]


