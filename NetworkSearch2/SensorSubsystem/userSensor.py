""" Contain UserSensor class.

This module contains a UserSensor class used
for detect system user information.

@author: Thanakorn Sueverachai
"""

import time
import logging
import pwd, grp

from NetworkSearch2.SensorSubsystem.genericSensor import GenericSensor

REFRESH_RATE = 20

class UserSensor(GenericSensor):
    """ The sensor for detecting a username."""
    
    def __init__(self):
        super(UserSensor,self).__init__()
        logging.info("Initiated")
        
    def run(self):
        """ Overwrite GenericSensor.run() method. This method will be called when the sensor started"""
        while 1:
            
            #######################
            # collect information #
            #######################
            
            user_dict = {}
            
            # loop through users
            for user in pwd.getpwall():
                # collect information
                user_object = {'object-type'    : 'user',
                        'object-name'    : 'ns:'+user.pw_name,
                        'user-id'        : user.pw_uid,
                        'directory'      : user.pw_dir,
                        'shell'          : user.pw_shell,
                        'group'          : [grp.getgrgid(user.pw_gid).gr_name],
                        'comment'        : filter(None, user.pw_gecos.split(',')) # split ',' and remove blank space
                        }
                
                # remove comment field if there is nothing
                if not user_object['comment']:
                    del user_object['comment']
                
                ############################
                # added to key-value store #
                ############################
                # add user object into a class dict variable
                user_dict['ns:'+user.pw_name] = user_object
                
            # loop through groups
            for g in grp.getgrall():
                # each member in a group
                for uname in g.gr_mem:
                    # add group name into a user objects
                    user_dict['ns:'+uname]['group'].append(g.gr_name)
                    
            #####################
            # update and delete #
            #####################  
                       
            # call super's function to perform updating and deleting
            self.updates_and_deletes(user_dict)

            #######################
            # sleep for some time #
            #######################         
            time.sleep(REFRESH_RATE)
            
             
if __name__=="__main__":
  
    u = UserSensor()
    from NetworkSearch2.SensorSubsystem.dbConnector import DBConnector
    u.bind_connector(DBConnector())
    u.start()
    time.sleep(100)
