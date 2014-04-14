""" Contain UserSensor class.

This module contains a UserSensor class used
for detect system user information.

@author: Thanakorn Sueverachai
"""

import time
import logging
import pwd, grp
import json
import sys
import datetime 
from onePConnect import OnePConnect
from onep.vty.VtyService import VtyService
from onep.core.exception import OnepRemoteProcedureException, OnepException
from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor

REFRESH_RATE = 5


class VTY(OnePConnect):
	'''
		onepk libraryy for VTY
	'''



class OnePVTYSensor(GenericSensor):
    """ The sensor for detecting a username."""
    
    def __init__(self):
        super(OnePVTYSensor,self).__init__()
        logging.info("Initiated")
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
        while 1:
            
            #######################
            # collect information #
            #######################
            ios_commands = ['show version', 'show flash:', 'show arp','show run | sec username','show run | sec line', 'show run | sec interface','show ip route','show interface stats'] 
            vty_dict = {}
            vty_pre_dict = {}
            vty = VTY(list())
            vty.set_transport('tcp')
            vty.set_username('cisco')
            vty.set_password('cisco')
            vty.set_element_address('10.1.0.1')
            try:
                vty.connect('vty')
                vtyService = VtyService(vty.get_network_element())
                vtyService.open()
                for ios_command in ios_commands:
                    vty_pre_dict={}
                    vty_result = vtyService.write(ios_command)
                    normalize_commmand = ios_command
                    ns_name = 'ns:%s:%s' % (vty.get_element_addr(), ios_command)
                    vty_pre_dict['object-name'] = ns_name
                    vty_pre_dict['object-type'] = 'sh-command'
                    vty_pre_dict['object-location']='172.20.127.233'
                    vty_pre_dict['location-type']='network'
                    vty_pre_dict['search-node'] = '172.20.127.235'
                    vty_pre_dict['timestamp'] = datetime.datetime.now()
                    vty_pre_dict['raw-output'] = vty_result
                    vty_dict[ns_name]=vty_pre_dict

                vtyService.close()
                vtyService.destroy()
                vty.disconnect()
            except:
                logging.error("OnePK gets error")
                time.sleep(1)
                continue
            
			#####################
            # update and delete #
            #####################  
            # call super's function to perform updating and deleting

            self.updates_and_deletes(vty_dict)

            #######################
            # sleep for some time #
            #######################         
            time.sleep(REFRESH_RATE)
           
             
if __name__=="__main__":
  
    u = OnePVTYSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    u.bind_connector(DBConnector())
    u.start()
    time.sleep(100)
