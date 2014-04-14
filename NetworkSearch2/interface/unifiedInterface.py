
import platform
import time
import cPickle as pickle

import zmq


from NetworkSearch2.interpreter.interpreter import interpreter
from NetworkSearch2.QuerySubsystem.queryObject import QueryObject
import logging

HOST = platform.uname()[1]
EXTERNAL_PORT = 7735

class interface():    
    def __init__(self, queryExpression, specified_parameters):
        
        # default parameters
        parameters = {'limit':None ,'isApprox':True, 'tf':5,'nr':5,'tr':5,'ks':5,'ds':5,'fs':5,'vicinity-precision':False,'hop':1}
        parameters.update(specified_parameters)
        self.parameters = parameters
        self.queryExpression = queryExpression
		
        try:
            self.weightScore = { "tf" : int(parameters['tf']),
					             "nr" : int(parameters['nr']),
                                 "tr" : int(parameters['tr']),
                                 "ks" : int(parameters['ms']),
                                 "ds" : int(parameters['ds']),
                                 "fs" : int(parameters['fs'])
                            } 
        except ValueError:
            self.weightScore = { "tf" : 5,
                                 "nr" : 5,
                                 "tr" : 5,
                                 "ks" : 5,
                                 "ds" : 5,
                                 "fs" : 5
                                }
            self.parameters['tf'] = 5
            self.parameters['nr'] = 5
            self.parameters['tr'] = 5
            self.parameters['ks'] = 5
            self.parameters['ds'] = 5
            self.parameters['fs'] = 5
        
        self.isApprox = parameters['isApprox']
        self.vicinity_precision = parameters['vicinity-precision']
        try:
            self.limit = int(parameters['limit'])
        except ValueError:
            self.limit = None
            self.parameters['limit'] = None
        
        try:
            self.hop = int(parameters['hop'])
        except ValueError:
            self.hop = 1
            self.parameters['hop'] = 1

        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % EXTERNAL_PORT)
         
    def search(self):
        self.dbQuery = ""
        
        t0 = time.time()
        # parse user query
        match_query,flags,vicinity_param,mq = interpreter(self.queryExpression, self.isApprox)
        
        vicinity_param['location'] = '110 West Tasman Drive San Jose 95134 California'
		
        # normal execution
        self.basic(match_query,flags,vicinity_param)   
        self.clean_up_result()
        self.numResults = len(self.results)
        self.time = time.time()-t0
        self.mq = mq
        self.vicinity_param = vicinity_param
    
    def clean_up_result(self):
        results =self.results
        name_list = ['tf_score','nr_score','tr_score','tf','nr','tr','keyword' , 'document','_id', 'hop']
        for obj in results:
            for key_name in name_list:
                if obj.has_key(key_name):
                    del obj[key_name]
        temp = []
        for obj in results:
            try:
                temp.append((obj['total_score'],obj))
                del obj['total_score']
            except KeyError:
                break
        else: # execute when for loop finish without break
            self.results = temp

    
    def basic(self,match_query,flags,vicinity_param):
        """basic query execution"""

        if not match_query:
            self.results = ""
            return
        if 'approximate' in flags:
            q = QueryObject(match_query,parameters={'isRank':True,"limit":self.limit,"isApprox":True,"weightScore":self.weightScore,"vicinity-precision":self.vicinity_precision,"hop":self.hop,"isVicinity":flags['vicinity'],"vicinity":vicinity_param})
            self.socket.send_pyobj(q)
            self.parameters['isApprox'] = True
        elif 'exact' in flags:    
            #print "exact : " + `match_query`
            self.socket.send_pyobj(QueryObject(match_query,parameters={'isRank':False,"isApprox":False}))
            self.parameters['isApprox'] = False         
        else:
            #print "ERROR : unknown query"
            self.results = [{'Error':'unknown query'}]
            return
        
        # receive pickled dict
        self.results = pickle.loads(self.socket.recv())
