""" contains QueryObject class.

It defines the QueryObject class. It contains the query information.
e.g. query statements, some specific parameters for an execution, etc.
It is served for being an data object.

@author: Thanakorn Sueverachai
"""

from pprint import pformat

class QueryObject(object):
    """ The query object. """
        
    def __init__(self, match_statement, parameters = {}):
    
        # collect information
        self.match_statement = match_statement
        
        default_parameters = {
                              "limit" : None,
                              "isRank" : True,
                              "isApprox" : True,
                              "weightScore" : { "tf" : 5,
                                                "nr" : 5,
                                                "tr" : 5,
                                                "ks" : 5,
                                                "ds" : 5,
                                                "fs" : 5
                                              },
                              "vicinity-precision":False,
                              "hop": 1,
							  "isVicinity":False,
							  "vicinity":{"distance_measure":None,"distance_unit":None,"location":None}
                              }
        self.parameters = default_parameters
        self.parameters.update(parameters)
    def __str__(self):
        # for better presentation
        return pformat(self.__dict__)

