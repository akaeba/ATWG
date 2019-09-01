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
        # some preparation
        mySample = 2
        myPeriod = 1800
        # create class
        myWaves = waves.waves()
        # Init with max amp, phase=90deg
        self.assertTrue(myWaves.sine_init(sample=mySample, period=myPeriod, low=-20, high=20, init=20, posSlope=True))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)     #
        self.assertEqual(myWaves.iterator, 1/4 * (myPeriod / mySample))
        # Init with min amp, phase=270deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=-20, posSlope=True))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 3/4 * (myPeriod / mySample))
        # Init with middle value, phase=0deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=0, posSlope=True))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 0 * (myPeriod / mySample))
        # Init with middle value, phase=180deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=0, posSlope=False))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 1/2 * (myPeriod / mySample))
    #*****************************
    
    
    #*****************************
    def test_sine(self):
        # some preparation
        mySample = 2
        myPeriod = 1800
        lowVal = 0
        highVal = 20
        initVal = (highVal - lowVal) / 2
        # init sine
        myWaves = waves.waves()
        self.assertTrue(myWaves.sine_init(sample=mySample, period=myPeriod, low=lowVal, high=highVal, init=initVal, posSlope=True))
        self.assertEqual(myWaves.iterator, 0 * (myPeriod / mySample))
        # check sine
        
        
        
        
    

        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
