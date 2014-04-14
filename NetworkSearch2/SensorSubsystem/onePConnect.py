#!/usr/bin/env python

# Copyright (c) 2010-2013 by Cisco Systems, Inc.
# 
# THIS SAMPLE CODE IS PROVIDED "AS IS" WITHOUT ANY EXPRESS OR IMPLIED WARRANTY
# BY CISCO SOLELY FOR THE PURPOSE of PROVIDING PROGRAMMING EXAMPLES.
# CISCO SHALL NOT BE HELD LIABLE FOR ANY USE OF THE SAMPLE CODE IN ANY
# APPLICATION.
# 
# Redistribution and use of the sample code, with or without
# modification, are permitted provided that the following conditions
# are met:
# Redistributions of source code must retain the above disclaimer.

"""
The goal of the BaseTutorial is to show how to create an application and connect to a network element to obtain a
session handle. The BaseTutorial provides base class functions for reading test properties, parsing command line
properties, and network element connectivity.

@author The onePK Team (onepk-feedback@cisco.com)

"""
from onep.element.NetworkElement import NetworkApplication, NetworkElement
from onep.interfaces.InterfaceStatus import InterfaceStatus
from onep.element.SessionConfig import SessionConfig

import getopt
import sys
import getpass
import onep.interfaces.InterfaceFilter
import os

#  START SNIPPET: createLogger
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('onep:BaseTutorial')
logger.setLevel(logging.INFO)
#  END SNIPPET: createLogger

class OnePConnect(object):
    #  START SNIPPET: variables
    element_address = None
    username = None
    password = None
    transport = "tls"
    network_element = None
    session_handle = None
    root_cert_path = None
    
    args = None
    #  END SNIPPET: variables

    def __init__(self, args):
        """
        Instantiates the Logger instance using the classname of the implementing class.
        """
        self.args = args

    def connect(self, applicationName):
        """
        Obtains a NetworkApplication instance, sets the name to applicationName, gets a network element for the IP
        address in the command line arguments or tutorial.properties file - both via the string format and an InetAddress
        formed from the IP address string - and then tries to connect to the Network Element with the username and
        password supplied, or from the tutorial.properties file.
        
        @param applicationName: The NetworkApplication name is set to this value.
        @return True if the connection succeeded without exception, else false.
        @throws OnepException
        """
        
        #  START SNIPPET: init_myapp
        network_application = NetworkApplication.get_instance()
        #  END SNIPPET: init_myapp
        
        #  START SNIPPET: name_myapp   
        network_application.name = applicationName
        #  END SNIPPET: name_myapp
        
        #  START SNIPPET: get_ne_opt1
        self.network_element = network_application.get_network_element(self.element_address)
        #  END SNIPPET: get_ne_opt1
        if self.network_element == None:
            logger.error("Failed to get network element")
            sys.exit(1)

        logger.info("We have a NetworkElement : " + self.network_element.__str__())
        
        #  START SNIPPET: connect
        session_config = SessionConfig(SessionConfig.SessionTransportMode.TLS) #default is TLS
        if self.transport.lower() == "tcp" or self.transport == "0":
            session_config = SessionConfig(SessionConfig.SessionTransportMode.SOCKET)
        elif self.transport.lower() == "tipc" or self.transport == "2":
            session_config = SessionConfig(SessionConfig.SessionTransportMode.TIPC)

        # Set the path to the root CA certificates
        session_config.caCerts = self.root_cert_path

        self.session_handle = self.network_element.connect(self.username, self.password, session_config)
        #  END SNIPPET: connect
        
        if self.session_handle == None:
            #  START SNIPPET: loggerError
            logger.error("Failed to connect to NetworkElement - ")
            #  END SNIPPET: loggerError
            return False
        logger.info("Successful connection to NetworkElement - " )
        return True

    def disconnect(self):
        """
        Disconnects the application from the Network Element.
        
        @return True if the disconnect succeeded without an exception, else false if the application failed to disconnect
        from the Network Element.
        """
        try:
            if self.network_element.is_connected():
                self.network_element.disconnect()
        except Exception, e:
            logger.error("Failed to disconnect from Network Element")
            logger.error(e)
            return False
        return True

    def get_element_addr(self):
        """
        Gets the IP address or hostname of the Network Element set during instantiation.
        
        @return The element_address.        
        """
        return self.element_address


    def get_element_inet_address(self):
        """
        Gets the element_address, the Network Element's address or hostname, as an InetAddress.
               
        @return The element_address as an InetAddress.
        
        @throws UnknownHostException
        
        If the IP address of the NetworkElement cannot be resolved to a host.
        """    
        return self.element_address


    #  START SNIPPET: getLogger
    def get_logger(self):
        """
        Implements the logger, which sends all enabled log messages.
        
        @return The logger.
        """
        return self.logger
    #  END SNIPPET: getLogger
    

    def get_network_element(self):
        """
        Gets the NetworkElement that is being connected to by the application.
        
        @return The NetworkElement that is being connected to by the application.
        """
        return self.network_element

    def get_session_handle(self):
        """
        Gets the session_handle that identifies the connection to this Network Element.
        
        @return The session_handle that identifies the connection to this NetworkElement.
        """
        return self.session_handle

    def get_username(self):
        """
        Gets the username on whose behalf the connection will be made. The username is specified via the command line         
        @return The username that is specified via the command line or in the tutorial.properties file.
        """
        return self.username
    
    def get_password(self):
        """
        Gets the password with which connection will be made. The password is specified via the command line         
        @return The password that is specified via the command line or in the tutorial.properties file.
        """
         
        return self.password
    
    def get_transport(self):
        """
        Gets the transport mode with which connection will be made. The transport is specified via the command line         
        @return The transport that is specified via the command line or in the tutorial.properties file.
        """
        return self.transport
    
    def get_caCerts(self):
        """
        Gets the ROOT CA certificate. The certificate is specified via the command line
        """
        return self.root_cert_path
    
    def get_usage(self):
        return " Usage: -a <address> [-t <transport>] [-R <root certificates file>]"

    def parse_command_line(self, skip_login_for_tipc=True):
        """
        Parse the command line options.

        @param args  The args string passed into the main(...) method.
        
        @return true if parsing the command line succeeds, false otherwise.
        """
        try:
            opts, args = getopt.getopt(self.args[1:],"ha:t:R:",["address=","transport=", "rootcert="])
        except getopt.GetoptError as err:
            print str(err)
            logger.info(self.get_usage())
            sys.exit(2)
        
        """
         * options:
         *       -a, --address <network element address>
         *       -t, --transport <transport type> default is tls
         *       -R, --rootcert <root certificates file>
        """     
        for option, arg in opts:
            if option == '-h':
                logger.info(self.get_usage())
                sys.exit()
            elif option in ("-a", "--address"):
                self.element_address = arg
            elif option in ("-t", "--transport"):
                self.transport = arg
            elif option in ("-R", "--rootcert"):
                self.root_cert_path = arg
        
        if self.element_address == None:
            logger.error(self.get_usage())
            return False

        if self.transport != "tipc" or not skip_login_for_tipc:
            self.username = raw_input('Enter Username : ')
            self.password = getpass.getpass('Enter Password : ')
            if self.username == None or self.password == None:
                logger.error("Username and password are required.")
                return False
        
        return True

    def set_element_address(self, element_address):
        """
        """
        self.element_address = element_address

    def set_logger(self, logger):
        """
        """
        self.logger = logger

    def set_network_element(self, network_element):
        """
        """        
        self.network_element = network_element

    def set_password(self, password):
        """
        """        
        self.password = password

    def set_session_handle(self, session_handle):
        """
        """        
        self.session_handle = session_handle

    def set_username(self, username):
        """
        """        
        self.username = username

    def get_all_interfaces(self):
        """
        """        
        interfaceList = None
        try:
            interfaceList = self.network_element.get_interface_list(onep.interfaces.InterfaceFilter.InterfaceFilter())
        except Exception, e:
            logger.error(e)
        return interfaceList

    def get_an_interface(self):
        """
          Get an interface which has an IP addr set and which is not the interface that the application is connected to
        """
        interfaceList = None
        networkInterface = None
        skipFirst = False
        try:
            interfaceList = self.network_element.get_interface_list(onep.interfaces.InterfaceFilter.InterfaceFilter())
            elemAddre = self.network_element.host_address
            for networkInterface in interfaceList:
                addresses = networkInterface.get_address_list()
                for address in addresses:
                    if address != None:
                        if address != elemAddre:
                            if skipFirst:
                                return networkInterface
                            else: 
                                skipFirst = True                                
        except Exception, e:
            logger.error(e)
        return None 
    
    def get_an_up_interface(self):
        """
          Get an interface which has its LINK status as UP
        """
        interfaceList = None
        networkInterface = None
        try:
            interfaceList = self.network_element.get_interface_list(onep.interfaces.InterfaceFilter.InterfaceFilter())
            for networkInterface in interfaceList:
                if networkInterface.get_status().link == InterfaceStatus.InterfaceState.ONEP_IF_STATE_OPER_UP:
                    return networkInterface                          
        except Exception, e:
            logger.error(e)
        return None 

    def set_transport(self, transport):
        self.transport = transport
        
if __name__ == '__main__':
    tutorial = BaseTutorial(sys.argv)
    
    tutorial.set_password('cisco')
    tutorial.set_username('cisco')
    tutorial.set_transport('tcp')
    tutorial.set_element_address('10.1.0.1')
    
    logger.info("Connecting to Network Element...")
    try:
        tutorial.connect("BaseTutorial")
    except Exception, e:
        #logger.error("Error in connecting to network element - %s", e)
        logger.error(e)
        
    tutorial.disconnect()
    logger.info("Done.")
