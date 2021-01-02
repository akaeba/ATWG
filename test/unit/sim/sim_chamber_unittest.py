# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

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
import math       # for isnan

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../../"))) # add project root to lib search path   
import ATWG.driver.sim.sim_chamber as sim_chamber                                             # Python Script under test
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
        self.assertTrue(dut.open())
    #*****************************
    
    
    #*****************************
    def test_start(self):
        """
        @note   test open of sim class
        """
        dut = sim_chamber.simChamber()      # create class
        self.assertTrue(dut.start())
    #*****************************
    
    
    #*****************************
    def test_stop(self):
        """
        @note   test open of sim class
        """
        dut = sim_chamber.simChamber()      # create class
        self.assertTrue(dut.stop())
    #*****************************
    
    
    #*****************************
    def test_info(self):
        """
        @note:  checks chamber info function
        """
        dut = sim_chamber.simChamber()
        self.assertDictEqual(dut.info(), {'fracs': {'temperature': 2, 'humidity': 2}, 'name': 'SIM'})
    #*****************************
    
    
    #*****************************
    def test_get_clima(self):
        """
        @note:  test function
        """
        dut = sim_chamber.simChamber()  # create class
        dut.last_set_temp = 25          # set test data
        clima = dut.get_clima()
        self.assertTrue(math.isnan(clima['humidity']))
        self.assertEqual(clima['temperature'], 25)
    #*****************************
    
    
    #*****************************
    def test_set_clima(self):
        """
        @note:  test function
        """
        # prepare
        dut = sim_chamber.simChamber()  # create class
        # check for exception, missing value
        with self.assertRaises(ValueError) as cm:
            dut.set_clima()
        self.assertEqual(str(cm.exception), "No new data provided")
        # check for exception, set temp missing
        with self.assertRaises(ValueError) as cm:
            dut.set_clima(clima={})
        self.assertEqual(str(cm.exception), "Miss temperature set value")
        # succesfull set
        dut.set_clima(clima={'temperature': 20.5})
        self.assertEqual(dut.last_set_temp, 20.5)
    #*****************************
    
#------------------------------------------------------------------------------    



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
    