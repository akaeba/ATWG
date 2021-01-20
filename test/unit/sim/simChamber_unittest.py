# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          simChamber_unittest.py
@date:          2020-02-22

@note           Unittest for simChamber.py
                  run ./test/unit/sim/simChamber_unittest.py
"""



#------------------------------------------------------------------------------
# Libs
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test
import math       # for isnan
# Self, DUT
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../../"))) # add project root to lib search path   
from ATWG.driver.sim.simChamber import simChamber                                             # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class TestSimChamber(unittest.TestCase):
    
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
        dut = simChamber()      # create class
        self.assertTrue(dut.open())
    #*****************************
    
    
    #*****************************
    def test_start(self):
        """
        @note   test open of sim class
        """
        dut = simChamber()      # create class
        self.assertTrue(dut.start())
    #*****************************
    
    
    #*****************************
    def test_stop(self):
        """
        @note   test open of sim class
        """
        dut = simChamber()      # create class
        self.assertTrue(dut.stop())
    #*****************************
    
    
    #*****************************
    def test_info(self):
        """
        @note:  checks chamber info function
        """
        dut = simChamber()
        info = dut.info()
        self.assertDictEqual(info['fracs'], {'temperature': 2, 'humidity': 2})
        self.assertDictEqual(info['temperature']['ratings'], {'min': float('-inf'), 'max': float('+inf'), 'unit': 'c'})
        self.assertDictEqual(info['temperature']['slewrate'], {'rise': float('+inf'), 'fall': float('-inf'), 'unit': 'c/min'})
        self.assertEqual(info['name'], "SIM")
    #*****************************
    
    
    #*****************************
    def test_get_clima(self):
        """
        @note:  test function
        """
        dut = simChamber()      # create class
        dut.last_set_temp = 25  # set test data
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
        dut = simChamber()    # create class
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
    