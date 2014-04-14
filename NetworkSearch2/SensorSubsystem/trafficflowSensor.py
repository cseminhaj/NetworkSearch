""" 
@author: Misbah Uddin
"""

import time
import logging
import json
import urllib

from collections import defaultdict
from datetime import datetime
from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor
   

class TrafficflowSensor(GenericSensor):
    """ The sensor for detecting virtual machines."""

    def __init__(self):
        super(TrafficflowSensor,self).__init__()
        logging.info("Initiated")
        
        # VM no longer exists
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""

        sp = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/parking-sensors.csv','r')      
        parking_data =defaultdict(defaultdict)
        for line in sp:
            line = line.strip('\n').split(',')
            temp_dict = {}
            temp_dict['object-name'] = 'ns:'+line[0]
            temp_dict['object-location'] = line[2].split('lot')[0].strip()
            parking_data[temp_dict['object-name']]=temp_dict
        sp.close()
        #for k,v in parking_data.items():
        #    print v['object-name']
        
        psp = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/flow-sensors.csv','r')

        flow_data =defaultdict(defaultdict)
        tag = 0

        for line in psp:
            line = line.strip('\n').split(',')
            temp_dict = {}
            temp_dict['object-name'] = 'ns:'+line[0]
            temp_dict['object-type'] = 'traffic-sensor'
            temp_dict['object-location'] = line[2]
            temp_dict['location-type'] = 'geographic'
            temp_dict['timestamp'] = datetime.now()
            temp_dict['traffic-volume'] = line[4]
            temp_dict['traffic-volume-average'] = line[5]
            #for k,v in parking_data.items():
            #    url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={'+temp_dict['object-location']+'}&destinations={'+v['object-location']+'}&mode=driving&language=en-EN&sensor=false'
            #    result = json.load(urllib.urlopen(url))
             #   distance = int(result['rows'][0]['elements'][0]['duration']['value'])
                #print distance,v['object-name']
              #  if distance < 30:
                      #print distance, temp_dict['object-location'], v['object-location'],v['object-name']
               #    if 'parking-sensors' not in temp_dict:
                #            temp_dict['parking-sensors'] = [v['object-name']]
                            #print temp_dict['parking-sensors']
                 #  else:
                  #     tmp = temp_dict['parking-sensors']
                   #    tmp.append(v['object-name'])
                    #   temp_dict['parking-sensors'] = tmp
            #print "trafficflowSensor>> flow-sensor: ",temp_dict
            flow_data[temp_dict['object-name']]=temp_dict
        pt = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/flow-trace.csv','r')

        k=0
        dat = []
        for line in pt:
            dat.append(line)
            k=k+1
        pt.close()
        j = 0
        
        while 1:
            flow_dict = flow_data
            ######################
            # perform collection #
            ######################
            line = dat[j].strip('\n').split(';')
            sleep_time = float(line[0])
            temp = line[1].split(',')
            num_sensor = len(temp)/4
            for i in range(num_sensor):
                id = temp[4*i].replace("[","").replace("]","").replace("'","").lstrip(' ')
                id = 'ns:'+id
                flow_data[id]['timestamp']=datetime.now()
                if temp[4*i+2].replace("[","").replace("]","").replace("'","").lstrip(' ') == 'vehicle_volum':
			        flow_data[id]['traffic-volume']=temp[4*i+3].replace("[","").replace("]","").replace("'","").lstrip(' ')
                elif temp[4*i+2].replace("[","").replace("]","").replace("'","").lstrip(' ') == 'vehicle_occupation_average':
                    flow_data[id]['traffic-volume-average']=temp[4*i+3].replace("[","").replace("]","").replace("'","").lstrip(' ')
                flow_dict[id] = flow_data[id]
            j = j + 1
            if j == k-1: j = 0               
            #####################
            # update and delete #
            #####################  
            # call super's function to perform updating and deleting
            self.updates_and_deletes(flow_dict)
            #######################
            # sleep for some time #
            #######################
            #time.sleep(REFRESH_RATE)
            time.sleep(sleep_time)

if __name__=="__main__":
  
    f = TrafficflowSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    f.bind_connector(DBConnector())
    f.start()
    time.sleep(100)
