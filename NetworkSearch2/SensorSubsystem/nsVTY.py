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
# 
# package: tutorials.vty
import logging
from onePConnect import OnePConnect
from onep.vty.VtyService import VtyService
from onep.core.exception import OnepRemoteProcedureException, OnepException

logger = logging.getLogger('onep:VTYTutorial')
logger.setLevel(logging.INFO)

class VTYT(OnePConnect):
    """
    This tutorial shows how to create VTY Service on a ONEP Application 
    and demonstrates the capability to communicate with a Network Element via virtual terminal. .

    @author The onePK Team (onepk-feedback@cisco.com)
    """

    def show_parser_state_attributes(self, parser_state):
        """
        This method prints the attributes of the ParserState and iterates over the command results
        
        @param parser_state
        """
        #  START SNIPPET: vty_parser_state_attribs
        logger.info("ParserState prompt - %s", parser_state.prompt)
        logger.info("ParserState overallrc - %s", parser_state.overallRC)
        cmd_results = parser_state.results
        for cmd_result in cmd_results:
            logger.info("ParserState::cmdresult:inputline - %s", cmd_result.input_line)
            logger.info("ParserState::cmdresult:parsereturncode - %s", cmd_result.parse_return_code)
            logger.info("ParserState::cmdresult:errorlocation - %s", cmd_result.error_location)
        #  END SNIPPET: vty_parser_state_attribs


if __name__ == '__main__':
    """
    Invokes the tutorial via the command line. This main method attempts to use arguments from the command line.
    """
    import sys
    tutorial = VTYT(sys.argv)
    tutorial.set_transport('tcp')
    tutorial.set_username('cisco')
    tutorial.set_password('cisco')
    tutorial.set_element_address('10.1.0.1')



    try:
        logger.info("Connecting to Network Element...")
        if not tutorial.connect("VTYTutorial"):
            logger.error("Error in connecting to network element")
            sys.exit(1)
        logger.info("Done")
        
        """Get a VTYService from the NE"""
        #  START SNIPPET: create_vty
        vtyService = VtyService(tutorial.get_network_element()) 
        #  END SNIPPET: create_vty
        
        """Open the VTY on the NE with the default command interpreter"""
        #  START SNIPPET: open_vty
        vtyService.open()
        #  END SNIPPET: open_vty

        """Write a string to the VTY on NE"""
        #TEST_CMD2 = "show arp"
        #TEST_CMD2 = "show flash:"
        #TEST_CMD2 = "show adjacency"
        #TEST_CMD2 = "sh run | sec router"
        #TEST_CMD2 = "sh run | sec username"
        #TEST_CMD2 = "sh run | sec line"
        #TEST_CMD2 = "sh run | sec interface"
        #TEST_CMD2 = "sh run | sec router ospf"
        #TEST_CMD2 = "sh run | sec router bgp"
        TEST_CMD2 = "sh run | sec version"
        logger.info("Test Command : %s", TEST_CMD2)
        logger.info("CLI Result for Test Command : %s", cli_result)

        

        """Cancel the command execution"""
        #  START SNIPPET: vty_cancel_cmd
        #vtyService.cancel()
        #  END SNIPPET: vty_cancel_cmd    
                
        """Close the VTY connection on NE"""
        #  START SNIPPET: vty_close            
        vtyService.close()
        #  END SNIPPET: vty_close            

        """Destroy the VTY"""        
        #  START SNIPPET: vty_destroy      
        vtyService.destroy()
        #  END SNIPPET: vty_destroy 
    except Exception, e:
        #  START SNIPPET: disconnect_ne
        tutorial.disconnect()
        #  END SNIPPET: disconnect_ne
        logger.error(str(e))
    tutorial.disconnect()
    sys.exit(0)

