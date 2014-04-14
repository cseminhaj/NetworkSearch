""" 
@author: Misbah Uddin
"""

import time
import logging
from collections import defaultdict
from datetime import datetime
from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor
    
class SyslogSensor(GenericSensor):
    """ The sensor for detecting virtual machines."""

    def __init__(self):
        super(SyslogSensor,self).__init__()
        logging.info("Initiated")
        
        # VM no longer exists
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
       
        from subprocess import PIPE, Popen
        from shlex import split
        tag = 0
        old_r = ''
        location = '172.20.127.233'
        while 1:
                cmd = 'tcpdump -v -i eth1' 
                p = Popen(split(cmd),stdout=PIPE) 
                syslog_dict = {}
                for row in p.stdout:
                    r = row
                    if ('syslog' in r):
                        tag = 1
                        segment = old_r
                        segment = segment + r
                    elif tag == 1:
                        tag = 2
                        segment = segment + r
                    elif tag == 2:
                        tag = 0
                        segment = segment + r
                        tm = datetime.now().isoformat()
                        name = '172.20.127.233'+':'+str(tm)
                        type = 'syslog'
                        syslog_dict[name]={'object-name':name,'object-type':type,'object-location':location,'location-type':'network','message-content':segment,'timestamp':datetime.now()}
                        self.updates_and_deletes(syslog_dict)
                    else:
                        old_r =r
            #except KeyboardInterrupt:
            #   p.terminate()
			######################
            # perform collection #
            # update and delete #
            #####################  
            # call super's function to perform updating and deleting
            #self.updates_and_deletes(parking_dict)
            #######################
            # sleep for some time #
            #######################
            #time.sleep(REFRESH_RATE)
            #time.sleep(sleep_time)

#if __name__=="__main__":
  
#    p = ParkingSensor()
#    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
#    p.bind_connector(DBConnector())
#    p.start()
#    time.sleep(100)
