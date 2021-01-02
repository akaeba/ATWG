# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          sim_chamber.py
@date:          2020-02-22
@version:       0.1.0

@note           virtual climate chamber, allows ATWG virtual run
"""


#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../")))  # add project root to lib search path    
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class simChamber:

    #*****************************
    def __init__(self):
        self.last_set_temp = 20.0
    #*****************************
    
    
    #*****************************
    def open(self, cfgFile=None):
        """
        @note           opens physical interface to chamber, dummy in sim
        
        @rtype          boolean
        @return         successfull opened
        """
        # Config file is meaningless in sim mode
        if ( None != cfgFile ):
            raise Warning("Interface configurtion File '" + os.path.basename(cfgFile) + "' skipped in sim mode")
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def close(self):
        """
        @note           closes physical interface, dummy in sim
        
        @rtype          boolean
        @return         successfull closed
        """
        return True
    #*****************************
    
    
    #*****************************
    def start(self, temperature=None):
        """
        @note           starts chamber, dummy in sim
        
        @rtype          boolean
        @return         successfull closed
        """
        if ( None != temperature ):
            self.last_set_temp = temperature
        return True
    #*****************************
    
    
    #*****************************
    def stop(self):
        """
        @note           stops chamber, dummy in sim
        
        @rtype          boolean
        @return         successfull closed
        """
        return True
    #*****************************
    
    
    #*****************************
    def info(self):
        """
        @note           Get Humidity and Temperature fracs resolution
        
        @rtype          dict
        @return         hudidity/temperature resolution
        """
        # build fracs dict
        fracs = {}
        fracs['temperature'] = 2   # temperature frac digits
        fracs['humidity'] = 2      # humidity frac digits
        # build final info structure
        info = {}
        info['fracs'] = fracs   # add
        info['name'] = "SIM"    # insert
        # release
        return info
    #*****************************
    
    
    #*****************************
    def get_clima(self):
        """
        @note           Current measured clima
        
        @rtype          dict
        @return         hudidity/temperature vals
        """
        clima = {}
        clima['temperature'] = self.last_set_temp
        clima['humidity'] = float('nan')
        return clima
    #*****************************    
    
    
    #*****************************
    def set_clima(self, clima=None):
        """
        @note           Current measured clima
        
        @rtype          boolean
        @return         hudidity/temperature vals
        """
        # check for arg
        if ( clima == None ):
            raise ValueError("No new data provided")
        # try to set temperature
        try:
            self.last_set_temp = clima['temperature']
        except:
            raise ValueError("Miss temperature set value")
        # try to set humidity
        # graceful end
        return True
    #*****************************
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':

    myChamber = simChamber()        # call class constructor
    myChamber.open()                # open with interface defaults
    myChamber.close()               # close chamber handle
#------------------------------------------------------------------------------
