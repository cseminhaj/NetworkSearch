""" 
@author: Misbah Uddin
"""

import time
import logging
from collections import defaultdict
from datetime import datetime
from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor
    
class ParkingSensor(GenericSensor):
    """ The sensor for detecting virtual machines."""

    def __init__(self):
        super(ParkingSensor,self).__init__()
        logging.info("Initiated")
        
        # VM no longer exists
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
        psp = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/parking-sensors.csv','r')

        parking_dict =defaultdict(defaultdict)
        tag = 0

        for line in psp:
            line = line.strip('\n').split(',')
            temp_dict = {}
            temp_dict['object-name'] = line[0]
            temp_dict['object-type'] = 'parking-sensor'
            temp_dict['object-location'] = line[2]
            temp_dict['location-type'] = 'geographic'
            temp_dict['cost']=line[3]
            temp_dict['parking-type']=line[4]	
            temp_dict['timestamp'] = datetime.now()
            temp_dict['status'] = line[6]
            parking_dict[temp_dict['object-name']]=temp_dict
        pt = open('/opt/NetworkSearch/NetworkSearch2/SensorSubsystem/parking-trace.csv','r')
        #print parking_data
        k=0
        dat = []
        for line in pt:
            dat.append(line)
            k=k+1
        pt.close()
        j = 0
        #print dat 
        
        while 1:
            #parking_dict = {} #parking_data
            ######################
            # perform collection #
            ######################
            line = dat[j].strip('\n').split(';')
            sleep_time = float(line[0])
            temp = line[1].split(',')
            num_sensor = len(temp)/3
            for i in range(num_sensor):
                id = temp[3*i].replace("[","").replace("]","").replace("'","").lstrip(' ')
                parking_dict[id]['timestamp']=datetime.now()
                parking_dict[id]['status'] = temp[3*i+2].replace("[","").replace("]","").replace("'","").lstrip(' ')
                if 'content' in parking_dict[id]:content = parking_dict[id]['content']
                else: content = []
                #print parking_dict[id]['object-name'],parking_dict[id]['status'],content
            #parking_dict = parking_data
            j = j + 1
            if j == k-1: j = 0               
            #####################
            # update and delete #
            #####################  
            # call super's function to perform updating and deleting
            #print parking_dict
            #print parking_dict['01000015e0e6b04a']
            #print sleep_time
            self.updates_and_deletes(parking_dict)
            #######################
            # sleep for some time #
            #######################
            #time.sleep(REFRESH_RATE)
            #time.sleep(3)
            time.sleep(sleep_time)

if __name__=="__main__":
  
    p = ParkingSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    p.bind_connector(DBConnector())
    p.start()
    time.sleep(100)
