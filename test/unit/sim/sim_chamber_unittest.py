# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          sim_chamber_unittest.py
@date:          2020-02-22
@version:       0.1.0

@note           Unittest for sim_chamber.py
                  run ./test/unit/sim/sim_chamber_unittest.py
"""



#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../../"))) # add project root to lib search path   
import driver.sim.sim_chamber as sim_chamber                                                  # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class simChamber(unittest.TestCase):
    
    #*****************************
    def setUp(self):
        """
        @note:  set-ups test
        """
        pass
    #*****************************
    
    
    #*****************************
    def test_open(self, cfgFile=None):
        """
        @note   test open of sim class
        """
        dut = sim_chamber.simChamber()      # create class
        self.assertEqual(dut.open(), True)
    #*****************************
    
    
#------------------------------------------------------------------------------    



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
    