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
import math       # required for isnan

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../")))  # add project root to lib search path    
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class simChamber:

    #*****************************
    def __init__(self):
        self.last_set_temp = float("nan")
    #*****************************
    
    
    #*****************************
    def open(self, cfgFile=None):
        """
        @note           opens physical interface to chamber, in sim mode w/o function
        
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
        @note           closes physical interface
        
        @rtype          boolean
        @return         successfull closed
        """
        return True
    #*****************************
    
    

    
    
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':

    myChamber = simChamber()        # call class constructor
    myChamber.open()                # open with interface defaults
    
    myChamber.close()               # close chamber handle
#------------------------------------------------------------------------------
