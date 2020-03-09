# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          atwg_unittest.py
@date:          2020-01-07
@version:       0.1.0

@note           Unittest for ATWG.py
                  run ./test/unit/atwg_unittest.py
"""



#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../../")))   # add project root to lib search path
import ATWG                                                                                     # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class TestATWG(unittest.TestCase):

    #*****************************
    def setUp(self):
        """
        @note   set-ups test
        """
    #*****************************


    #*****************************
    def test_time_to_sec(self):
        """
        @note   checks time string to second conversion
        """
        # init values
        dut = ATWG.ATWG()
        # check exception: no time string
        with self.assertRaises(ValueError) as cm:
            dut.time_to_sec()
        self.assertEqual(str(cm.exception), "No time string provided")
        # check time in secs and numeric
        self.assertEqual(dut.time_to_sec(60), 60)
        # check time strin in pure seconds
        self.assertEqual(dut.time_to_sec("145"), 145)
        # check positional strings, format 'd:h:m:s'
        self.assertEqual(dut.time_to_sec("::30"), 30)
        self.assertEqual(dut.time_to_sec("02:30"), 150)
        self.assertEqual(dut.time_to_sec("01:02:30"), 3750)
        self.assertEqual(dut.time_to_sec("1.5:::"), 129600)
        # check with time units
        self.assertEqual(dut.time_to_sec("2day 2h"), 180000)
        self.assertEqual(dut.time_to_sec("1.5day 2.5h"), 138600)
        # check without numeric base
        self.assertEqual(dut.time_to_sec("h"), 3600)
        self.assertEqual(dut.time_to_sec("min"), 60)
        self.assertEqual(dut.time_to_sec("sec"), 1)
    #*****************************
    
    
    #*****************************
    def test_sec_to_time(self):
        """
        @note   checks time string to second conversion
        """
        # init values
        dut = ATWG.ATWG()
        # check exception: no time string
        with self.assertRaises(ValueError) as cm:
            dut.sec_to_time()
        self.assertEqual(str(cm.exception), "No time provided")
        # check exception: neagtive number of seconds provided
        with self.assertRaises(ValueError) as cm:
            dut.sec_to_time(-25)
        self.assertEqual(str(cm.exception), "Only non-negativ secs allowed")
        # convert to string, blank separated
        self.assertEqual(dut.sec_to_time(129631), "1d 12h 31s")
        self.assertEqual(dut.sec_to_time(29), "29s")
        self.assertEqual(dut.sec_to_time(0), "0")
        self.assertEqual(dut.sec_to_time(61), "1m 1s")
        self.assertEqual(dut.sec_to_time(61.5), "1m 1.5s")
        # convert to string, colomn based
        self.assertEqual(dut.sec_to_time(sec=129731, sep=":"), "1:12:2:11")
    #*****************************
    
    
    #*****************************
    def test_temp_grad_to_time(self):  
        """
        @note   check slew temperature to slew time conversion function
        """    
        # init values
        dut = ATWG.ATWG()
        # check exception: no gradient
        with self.assertRaises(ValueError) as cm:
            dut.temp_grad_to_time()
        self.assertEqual(str(cm.exception), "No temperature gradient given")
        # check conversion
        self.assertEqual(dut.temp_grad_to_time(gradient="5sec", deltaTemp=None), 5)
        self.assertEqual(dut.temp_grad_to_time(gradient="2K/min", deltaTemp=10), 300)
    #*****************************
    
    
    #*****************************
    def test_parse_cli(self):
        """
        @note   checks parse command line interface function and it's processing
        """
        # init values
        dut = ATWG.ATWG()
        # check
        chamberArg, waveArg = dut.parse_cli(["--sine", "--riseTime=5sec", "--minTemp=5C", "--maxTemp=10c", "--chamber=ESPEC_SH641"])
        self.assertDictEqual(waveArg, {'ts': 1, 'tp': 3600, 'wave': 'sine', 'lowVal': 5, 'highVal': 10, 'tr': 5, 'initVal': 10})
        self.assertDictEqual(chamberArg, {'chamber': 'ESPEC_SH641', 'itfCfgFile': None})
    #*****************************
    
    
    #*****************************
    def test_normalize_gradient(self):
        """
        @note   checks normalize dividend
        """
        # init values
        dut = ATWG.ATWG()
        # check and convert
        self.assertDictEqual(dut.normalize_gradient(grad_sec=-0.04), {'val': -2.4, 'base': 'm'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=0.04), {'val': 2.4, 'base': 'm'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=1/3600), {'val': 1.0, 'base': 'h'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=-1/3600), {'val': -1.0, 'base': 'h'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=1/(24*3600)), {'val': 1.0, 'base': 'd'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=-1/(24*3600)), {'val': -1.0, 'base': 'd'})
        self.assertDictEqual(dut.normalize_gradient(grad_sec=0), {'val': 0, 'base': 's'})
    #*****************************
    
    
    #*****************************
    def test_open(self):
        """
        @note   tests open method
        """        
        # init values
        dut = ATWG.ATWG()
        # exception: no selection
        with self.assertRaises(ValueError) as cm:
            dut.open()
        self.assertEqual(str(cm.exception), "Missing args")
        # exception: unsupported chamber
        with self.assertRaises(ValueError) as cm:
            dut.open(chamberArg={'chamber': 'unknown', 'itfCfgFile': None}, waveArg={})
        self.assertEqual(str(cm.exception), "Unsupported climate chmaber 'unknown' selected")
        # exception: unsupported waveform
        with self.assertRaises(ValueError) as cm:
            dut.open(chamberArg={'chamber': 'SIM', 'itfCfgFile': None}, waveArg={'ts': 1, 'tp': 3600, 'wave': 'unknown'})
        self.assertEqual(str(cm.exception), "Unsupported waveform 'unknown' requested")
        # open in sim mode with sine wave
        self.assertTrue(dut.open(chamberArg={'chamber': 'SIM', 'itfCfgFile': None}, waveArg={'ts': 1, 'tp': 3600, 'wave': 'sine'}))
    #*****************************
    
    
    #*****************************
    def test_start(self):
        """
        @note   tests start function
        """ 
        # init values
        dut = ATWG.ATWG()
        # exception: not opend
        with self.assertRaises(ValueError) as cm:
            dut.start()
        self.assertEqual(str(cm.exception), "Interfaces not opened, call methode 'open'")
        # start chamber in sim mode
        self.assertTrue(dut.open(chamberArg={'chamber': 'SIM', 'itfCfgFile': None}, waveArg={'ts': 1, 'tp': 3600, 'wave': 'sine'}))
        self.assertTrue(dut.start())
    #*****************************
    
    
    #*****************************
    def test_stop(self):
        """
        @note   tests start function
        """ 
        # init values
        dut = ATWG.ATWG()
        # check, initVal added cause default comes from parse_cli
        self.assertTrue(dut.open(chamberArg={'chamber': 'SIM', 'itfCfgFile': None}, waveArg={'ts': 1, 'tp': 3600, 'wave': 'sine', 'initVal': 25}))
        self.assertTrue(dut.stop())
    #*****************************
    
    
    
    #*****************************
    def test_chamber_update(self):
        """
        @note   tests update function
        """
        pass
    
    
    
    
    #*****************************
    
    
    #*****************************
    def test_close(self):
        """
        @note   tests start function
        """ 
        # init values
        dut = ATWG.ATWG()
        # check
        self.assertTrue(dut.open(chamberArg={'chamber': 'SIM', 'itfCfgFile': None}, waveArg={'ts': 1, 'tp': 3600, 'wave': 'sine'}))
        self.assertTrue(dut.close())
    #*****************************  
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
