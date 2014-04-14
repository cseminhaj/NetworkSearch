""" 
@author: Misbah Uddin
"""

import time
import logging
from collections import defaultdict
from datetime import datetime
from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor
    
class GarbageSensor(GenericSensor):
    """ The sensor for detecting virtual machines."""

    def __init__(self):
        super(GarbageSensor,self).__init__()
        logging.info("Initiated")
        
        # VM no longer exists
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
        psp = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/garbage-sensors.csv','r')

        garbage_dict =defaultdict(defaultdict)
        tag = 0

        for line in psp:
            line = line.strip('\n').split(',')
            temp_dict = {}
            temp_dict['object-name'] = 'ns:'+line[0]
            temp_dict['object-type'] = 'garbage-sensor'
            temp_dict['object-location'] = line[2]
            temp_dict['location-type'] = 'geographic'
            temp_dict['timestamp'] = datetime.now()
            temp_dict['container-status'] = line[4]
            garbage_dict[temp_dict['object-name']]=temp_dict
        pt = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/garbage-trace.csv','r')

        k=0
        dat = []
        for line in pt:
            dat.append(line)
            k=k+1
        pt.close()
        j = 0
        
        while 1:
            #garbage_dict = garbage_data
            ######################
            # perform collection #
            ######################
            line = dat[j].strip('\n').split(';')
            sleep_time = float(line[0])
            temp = line[1].split(',')
            num_sensor = len(temp)/3
            for i in range(num_sensor):
                id = temp[3*i].replace("[","").replace("]","").replace("'","").lstrip(' ')
                id = 'ns:'+id  
                garbage_dict[id]['timestamp']=datetime.now()
                garbage_dict[id]['container-status']=temp[3*i+2].replace("[","").replace("]","").replace("'","").lstrip(' ')
                #garbage_dict[id] = garbage_data[id]
            j = j + 1
            if j == k-1: j = 0               
            #####################
            # update and delete #
            #####################  
            # call super's function to perform updating and deleting
            self.updates_and_deletes(garbage_dict)
            #######################
            # sleep for some time #
            #######################
            #time.sleep(REFRESH_RATE)
            time.sleep(sleep_time)

if __name__=="__main__":
  
    g = GarbageSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    g.bind_connector(DBConnector())
    g.start()
    time.sleep(100)
