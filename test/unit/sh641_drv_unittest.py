# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          sh641_drv_unittest.py
@date:          2019-12-22
@version:       0.1.0

@note           Unittest for sh641_drv.py
                  run ./test/unit/sh641_drv_unittest.py
"""



#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../"))) # add project root to lib search path   
import driver.espec.sh_641_drv as sh_641_drv                                               # Python Script under test
import driver.espec.sh_const as sh_const                                                   # climate chamber defintions
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class TestSh641(unittest.TestCase):
    
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
        dut = sh_641_drv.especShSu()                                                                                            # create class
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file
    #*****************************
    
    
    #*****************************
    def test_parse(self):
        """
        @note:  parse chamber reponses divides string into state, parm, val
                test check this
        """
        dut = sh_641_drv.especShSu()
        self.assertDictEqual(dut.parse("OK:TEMP,S25"), {'state': "OK", 'parm': "TEMP", 'val': "S25"})                                                                   # parse & check
        self.assertDictEqual(dut.parse("26.4,0.0,140.0,-50.0"), {'state': "OK", 'parm': "MEAS", 'val': {'measured': 26.4, 'setpoint': 0.0, 'upalarm': 140, 'lowalarm':-50}})   # parse & check
    #*****************************
        
        
    #*****************************
    def test_is_numeric(self):
        """
        @note:  if chamber feature not enabled, answer chmaber with an non-numeric
                string, needed for exception handling
        """
        dut = sh_641_drv.especShSu()
        self.assertFalse(dut.is_numeric(""))        # empty string
        self.assertTrue(dut.is_numeric(" -5.0"))    #
        self.assertTrue(dut.is_numeric("+6.0"))     #
    #*****************************
    
    
    #*****************************
    def test_get_temperature(self):
        """
        @note:  checks get temp request
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file
        self.assertTrue(dut.get_temperature() == 26.4)                                                                          # check
    #*****************************
    
    
    #*****************************
    def test_get_humidity(self):
        """
        @note:  checks get temp request
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file    
        self.assertTrue(dut.get_humidity() == 25)                                                                               # check
    #*****************************
    
    
    #*****************************
    def test_set_temperature(self):
        """
        @note:  test temperature setting function
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file 
        self.assertTrue(dut.set_temperature(35.21))
    #*****************************
    
    
    #*****************************
    def test_set_power(self):
        """
        @note:  test set power function
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file 
        self.assertTrue(dut.set_power())
        self.assertTrue(dut.set_power(pwr=sh_const.PWR_ON))
    #*****************************
    
    
    #*****************************
    def test_set_mode(self):
        """
        @note:  test set mode function
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file 
        self.assertTrue(dut.set_mode())
        self.assertTrue(dut.set_mode(mode=sh_const.MODE_CONSTANT))
        self.assertTrue(dut.set_mode(mode=sh_const.MODE_STANDBY))
        self.assertTrue(dut.set_mode(mode=sh_const.MODE_OFF))
    #*****************************
    
    
    #*****************************
    def test_start(self):
        """
        @note:  test chamber start function
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file 
        self.assertTrue(dut.start(temperature = -10))
        self.assertTrue(dut.start())
    #*****************************
    
    
    #*****************************
    def test_stop(self):
        """
        @note:  test chamber stop function
        """
        dut = sh_641_drv.especShSu()
        self.assertTrue(dut.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yml"))  # open dialog file
        self.assertTrue(dut.stop())
    #*****************************
    
    
    #*****************************
    def test_info(self):
        """
        @note:  checks chamber info function
        """
        dut = sh_641_drv.especShSu()
        self.assertDictEqual(dut.info(), {'fracs': {'temperature': 1, 'humidity': 1}, 'name': 'ESPEC_SH641'})
    #*****************************
    
#------------------------------------------------------------------------------    



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
