""" Contain UserSensor class.

This module contains a UserSensor class used
for detect system user information.

@author: Thanakorn Sueverachai
"""

import time
import logging
import pwd, grp
import requests
import json
import collections
import pprint

from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor

REFRESH_RATE = 20

def convert(data):
    if isinstance(data, basestring):
        return data.encode('ascii', errors='ignore')
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

class WeatherSensor(GenericSensor):
    """ The sensor for detecting a username."""
    
    def __init__(self):
        super(WeatherSensor,self).__init__()
        logging.info("Initiated")
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
        while 1:
            
            #######################
            # collect information #
            #######################
            
            weather_dict = {}

            cities = 'London SanFrancisco Tokyo Geneva NewYork'.split()
            for city in cities:
              url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city
              try:
                  result = requests.get(url)
              except:
                  logging.info("Connection Error")
                  continue
              wether_dic = convert(json.loads(result.text))
              pre_data = {}
              for k,v in wether_dic.items():
                if isinstance(v, dict):
                  pre_data = dict(pre_data.items() + v.items())
                elif isinstance(v, list):
                  for list_item  in v:
                    pre_data = dict(pre_data.items() + list_item.items())
                else:
                    pre_data = dict(pre_data.items() + [(k, v)])

              pre_data = dict(pre_data.items() + [('object-type', 'weather-sensor')])
              pre_data = dict(pre_data.items() + [('object-location', city + '.' + pre_data['country'])])
              pre_data = dict(pre_data.items() + [('object-name', 'ns:' + pre_data['name'].replace(' ',':'))])
              pre_data = dict(pre_data.items() + [('object-url',  url )])
              weather_dict[pre_data['object-name']] = pre_data
                    
            #####################
            # update and delete #
            #####################  
                       
            # call super's function to perform updating and deleting
            self.updates_and_deletes(weather_dict)

            #######################
            # sleep for some time #
            #######################         
            time.sleep(REFRESH_RATE)
            
             
if __name__=="__main__":
  
    u = WeatherSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    u.bind_connector(DBConnector())
    u.start()
    time.sleep(100)
