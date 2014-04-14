""" a executor class for an aggregator execution.

It defines an executor class used for an execution of
an aggregator in Echo protocol. In the executor class,
it has two method exposes to other modules, i.e., execute()
and aggregate(). The methods here are delegated from the Echo aggregator.

@author: Thanakorn Sueverachai
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
logging.basicConfig(filename='Executor.log',level=logging.DEBUG)

class executor:
    """ a class defines the execution of the aggragator for the echo protocol. """
    
    def __init__(self):
        self.mongo_connection = pymongo.MongoClient("127.0.0.1",27017)
        
    def _rank_aggregate(self,query):
        """(QueryObject) -> list of json object
        
        Calculate the total rank score for each object associated with the query.
        """
        ##############
        ## matching ##
        ##############
        collection = self.mongo_connection["index"]["termdoc"]
        
        with Profiler("index_DB_access_for_approx_match"):
            results_cursor = list(collection.find(query.match_statement))
       
        results = self._groupbyDoc(query,results_cursor)
        for i in results:
            logging.info(i)
        return results
        
    @Profiler.profile('Ranking')    
    def _groupbyDoc(self,query,results_cursor):
        
        ##########################
        ## grouping and ranking ##
        ##########################
        
        numbers_of_keyword = len(query.match_statement['$or'])
        
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
           
             result['total_score'] = (query.parameters['weightScore']['tf'] * result['tf_score']/float(numbers_of_keyword) + query.parameters['weightScore']['nr'] * result['nr_score']/float(numbers_of_keyword) + query.parameters['weightScore']['tr'] * result['tr_score']/float(numbers_of_keyword))/(query.parameters['weightScore']['tf']+query.parameters['weightScore']['nr']+query.parameters['weightScore']['tr'])
			#sum(query.parameters['weightScore'].itervalues())
                                    
             list_results.append(result)
        
        return list_results
    
    @Profiler.profile('Aggregator.local()')
    def execute(self,query):
        """ (QueryObject) -> list of json objects
        
        execute the local aggregator function. (similar to A.local() in echo context)
        """
        #########################
        # matching + projection #
        #########################
        
        # assign local variables
        object_collection = self.mongo_connection["sensor"]["objects"]
        limit = query.parameters['limit']

        if query.parameters['isApprox']:
            vicinity_tag = query.parameters['isVicinity']
            results = self._rank_aggregate(query)
            sorted_results = sorted(results, key=operator.itemgetter('total_score'),reverse=True)
            sorted_results = sorted_results[:limit]
            
            # get list of real-object oids from the index
            oid_list = map(operator.itemgetter('document'),sorted_results)
            with Profiler("object_DB_access_for_approx_match"):
                # get actual objects
                if oid_list:
                    #real_object_results = list(object_collection.find({"_id":{'$in':oid_list}},query.projection_statement))
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
                    logging.info(temp[obj_index['document']])
                except KeyError:
                    logging.warning("mismatch index object and real object : " + str(obj_index['document']))
            

            # ranking based on matching score, object distance, and freshnes
			# ranking_score = weight * matching_score + weight * distance_score + weight * freshness_score

            #print query.parameters['vicinity']
            # input for ranking signals 
            ks = float(query.parameters['weightScore']['ks'])
            ds = float(query.parameters['weightScore']['ds'])
            fs = float(query.parameters['weightScore']['fs'])
            
			
            if vicinity_tag == True:
               
               # normalize weights for ranking metrics
               kw = float(ks/(ks+ds+fs))
               dw = float(ds/(ks+ds+fs))
               fw = float(fs/(ks+ds+fs))
               #logging.info('Ranking Weights>> '+str(kw)+','+str(dw)+','+str(fw))
               
               current_time = datetime.now()
               time_ref = datetime(2014,03,17,8,0,0,0)
               distance_type = query.parameters['vicinity']['distance-unit']
               if (distance_type == 'minute') | (distance_type == 'minutes'): 
                    distance_threshold = int(query.parameters['vicinity']['distance-measure'])*60
                    dtype = 'duration'
               else:
                   distance_threshold = int(query.parameters['vicinity']['distance-measure'])
                   dtype = 'distance'
               distance_mode = query.parameters['vicinity']['distance-mode']
               if (distance_mode == 'walk'): distance_mode = 'walking'
               else: distance_mode = 'driving'
                              
               poi=query.parameters['vicinity']['location']
               
               if query.parameters['vicinity-precision'] == False: 
                       sn='110 West Tasman Drive San Jose 95134 California'
                       url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={'+poi+'}&destinations={'+sn+'}&mode='+distance_mode+'&language=en-EN&sensor=false'
                       result = json.load(urllib.urlopen(url))
                       distance_imprecise = int(result['rows'][0]['elements'][0][dtype]['value'])
                       distText_imprecise = result['rows'][0]['elements'][0][dtype]['text']
              
               for key,value in temp.items():			   
                   try:
                       if value['location-type']=='geographic':

                           if query.parameters['vicinity-precision'] == False:
                              distance = distance_imprecise
                              distText = distText_imprecise
                           else:
                              ob=value['object-location']
                              url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={'+poi+'}&destinations={'+ob+'}&mode='+distance_mode+'&language=en-EN&sensor=false'
                              result = json.load(urllib.urlopen(url))
                              distance = int(result['rows'][0]['elements'][0][dtype]['value'])
                              distText = result['rows'][0]['elements'][0][dtype]['text']
                              value['distance']=distText
                           
                           if distance < distance_threshold:
                              if distance == 0: distance_score = 1
                              else:distance_score = 1/float(distance)
                           else:
                               distance_score = 1/float(distance)*1/float(distance-distance_threshold)
                           object_time = value['timestamp']
                           freshness_score = (object_time - time_ref).total_seconds()/(current_time-time_ref).total_seconds()
                           keyword_score = temp[key]['total_score']
                           temp[key]['total_score']=((kw*keyword_score*2)+(dw*distance_score)+(fw*freshness_score))/3
                           logging.info(value['object-name']+','+value['object-type']+','+str(keyword_score)+','+str(distance_score)+','+str(freshness_score)+','+str(temp[key]))
                           #logging.info(value['object-name']+','+value['object-type']+','+str(keyword_score*kw)+','+str(distance_score*dw)+','+str(freshness_score*fw))
                           #temp[key]['total_score']=((kw*keyword_score*10)+(dw*distance_score)+(fw*freshness_score))/3
                       else:
                           object_time = value['timestamp']
                           distance_score = 0
                           freshness_score = (object_time - time_ref).total_seconds()/(current_time-time_ref).total_seconds()
                           keyword_score = temp[key]['total_score']
                           temp[key]['total_score']=((kw*keyword_score*2)+(dw*distance_score)+(fw*freshness_score))/3
                           #logging.info(value['object-name']+','+value['object-type']+','+value['location-type']+','+str(keyword_score)+','+str(distance_score)+','+str(freshness_score)+','+str(temp[key]))
                   except KeyError:
                       #logging.info(value['object-name']+','+value['location-type']+value['object-type']+','+str(keyword_score)+','+str(distance_score)+','+str(freshness_score))
                       pass
            else:
                 kw = float(ks/(ks+fs))
                 fw = float(fs/(ks+fs))
                 current_time = datetime.now()
                 time_ref = datetime(2014,03,17,8,0,0,0)
                 for key,value in temp.items():
                     object_time = value['timestamp']
                     freshness_score = (object_time - time_ref).total_seconds()/(current_time-time_ref).total_seconds()
                     keyword_score = temp[key]['total_score']
                     temp[key]['total_score'] = ((kw*keyword_score*2)+(fw*freshness_score))/2
            results = temp.itervalues()
            sorted_results = sorted(results, key=operator.itemgetter('total_score'),reverse=True)
            return sorted_results
        else:
            return []
    
    @Profiler.profile('Aggregator.aggregate()')
    def aggregate(self,local_result,agg,limit,aggregation_function_list):
        """ (QueryObject) -> list of json object 
        
        execute the aggregate function of an aggregator . (similar to A.aggregate() in echo context)
        """
        temp = local_result[:]
        temp.extend(agg)
        return sorted(temp, key=operator.itemgetter('total_score'),reverse=True)[:limit]
        
