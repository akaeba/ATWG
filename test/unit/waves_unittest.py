# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          waves_unittest.py
@date:          2019-08-25
@version:       0.1.0

@note           Unittest for waves.py
                  run ./test/unit/waves_unittest.py
"""



#------------------------------------------------------------------------------
import unittest         # performs test
import math             # check nan
from src import waves   # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class TestWaves(unittest.TestCase):
    
    #*****************************
    def setUp(self):
        """
        @note:  set-ups test
        """
    #*****************************
    
    
    #*****************************
    def test_divide(self):
        """
        @note:  tests zero divide divider function
        """
        myWaves = waves.waves()     # create class
        self.assertEqual(myWaves.divide(dividend=1, divisor=2), 0.5)        # normal devision
        self.assertTrue(math.isnan(myWaves.divide(dividend=1, divisor=0)))  # check divide by zero
    #*****************************
    
    
    #*****************************
    def test_clear_init(self):
        """
        @note:  tests clear_init function
        """
        myWaves = waves.waves()                 # create class
        self.assertTrue(myWaves.clear_init())   # clear init flags
        self.assertDictEqual(myWaves.sineDict, {'isInit': False})       # check
        self.assertDictEqual(myWaves.trapezoidDict, {'isInit': False})
    #*****************************
    
    
    #*****************************
    def test_sine_init(self):
        """
        @note:  tests sine init function
        """
        myWaves = waves.waves()     # create class
        self.assertTrue(myWaves.sine_init(sample=1, period=3600, low=-10, high=30, init=20))
        
        
        
        print("Iter:" + str(myWaves.iterator))
    
    #*****************************
    

        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
