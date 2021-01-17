# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          sh641_unittest.py
@date:          2019-12-22

@note           Unittest for sh641.py
                  run ./test/unit/sh641/sh641_unittest.py
"""



#------------------------------------------------------------------------------
# Standard
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test
# Self
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../../"))) # add project root to lib search path   
from ATWG.driver.espec.sh641 import especShSu                                                 # Python Script under test
from ATWG.driver.espec.sh641Const import *                                                    # climate chamber defintions
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class TestSh641(unittest.TestCase):
    
    #*****************************
    # common const
    simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_dialog.yml"
    print(simFile)
    #*****************************
    
    
    #*****************************
    def setUp(self):
        """
        @note:  set-ups test
        """
    #*****************************
    
    
    #*****************************
    def test_open(self):
        """
        @note:  checks the interface open function, for this test is identification
                of chamber redirected to a file
        """
        dut = especShSu()                                                                                            # create class
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file
    #*****************************
    
    
    #*****************************
    def test_parse(self):
        """
        @note:  parse chamber reponses divides string into state, parm, val
                test check this
        """
        dut = especShSu()
        self.assertDictEqual(dut.parse("OK:TEMP,S25"), {'state': "OK", 'parm': "TEMP", 'val': "S25"})                                                                   # parse & check
        self.assertDictEqual(dut.parse("26.4,0.0,140.0,-50.0"), {'state': "OK", 'parm': "MEAS", 'val': {'measured': 26.4, 'setpoint': 0.0, 'upalarm': 140, 'lowalarm':-50}})   # parse & check
    #*****************************
        
        
    #*****************************
    def test_is_numeric(self):
        """
        @note:  if chamber feature not enabled, answer chmaber with an non-numeric
                string, needed for exception handling
        """
        dut = especShSu()
        self.assertFalse(dut.is_numeric(""))        # empty string
        self.assertTrue(dut.is_numeric(" -5.0"))    #
        self.assertTrue(dut.is_numeric("+6.0"))     #
    #*****************************
    
    
    #*****************************
    def test_get_clima(self):
        """
        @note:  checks get temp request
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))                            # open dialog file
        self.assertDictEqual(dut.get_clima(), {'temperature': 26.4, 'humidity': 25})    # check
    #*****************************
    
    
    #*****************************
    def test_set_clima(self):
        """
        @note:  test temperature setting function
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file 
        self.assertTrue(dut.set_clima(clima={'temperature': 35.21}))
        self.assertTrue(dut.last_write_temp == 35.21)
    #*****************************
    
    
    #*****************************
    def test_set_power(self):
        """
        @note:  test set power function
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file 
        self.assertTrue(dut.set_power())
        self.assertTrue(dut.set_power(pwr=PWR_ON))
    #*****************************
    
    
    #*****************************
    def test_set_mode(self):
        """
        @note:  test set mode function
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file 
        self.assertTrue(dut.set_mode())
        self.assertTrue(dut.set_mode(mode=MODE_CONSTANT))
        self.assertTrue(dut.set_mode(mode=MODE_STANDBY))
        self.assertTrue(dut.set_mode(mode=MODE_OFF))
    #*****************************
    
    
    #*****************************
    def test_start(self):
        """
        @note:  test chamber start function
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file 
        self.assertTrue(dut.start(temperature = -10))
        self.assertTrue(dut.start())
    #*****************************
    
    
    #*****************************
    def test_stop(self):
        """
        @note:  test chamber stop function
        """
        dut = especShSu()
        self.assertTrue(dut.open(simFile=TestSh641.simFile))    # open dialog file
        self.assertTrue(dut.stop())
    #*****************************
    
    
    #*****************************
    def test_info(self):
        """
        @note:  checks chamber info function
        """
        dut = especShSu()
        self.assertDictEqual(dut.info(), {'fracs': {'temperature': 1, 'humidity': 1}, 'name': 'ESPEC_SH641'})
    #*****************************
    
#------------------------------------------------------------------------------    



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
