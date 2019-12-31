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
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test
import math       # check nan

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../")))  # add project root to lib search path   
import waves.waves as waves                                                                 # Python Script under test
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
        self.assertEqual(myWaves.divide(dividend=1, divisor=2), 0.5)                # normal devision
        self.assertTrue(float('inf') == myWaves.divide(dividend=1, divisor=0))      # check divide by zero
        self.assertTrue(float('-inf') == myWaves.divide(dividend=-1, divisor=0))    # check divide by zero
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
        mySample = 2    # sample time in seconds, every two seconds a new sample point
        myPeriod = 1800 # period in seconds
        # create class
        myWaves = waves.waves()
        # Init with max amp, phase=90deg
        self.assertTrue(myWaves.sine_init(sample=mySample, period=myPeriod, low=-20, high=20, init=20, posSlope=True))
        self.assertTrue(myWaves.sineDict.get('isInit',{}))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)     #
        self.assertEqual(myWaves.iterator, 1/4 * (myPeriod / mySample))
        # Init with min amp, phase=270deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=-20, posSlope=True))
        self.assertTrue(myWaves.sineDict.get('isInit',{}))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 3/4 * (myPeriod / mySample))
        # Init with middle value, phase=0deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=0, posSlope=True))
        self.assertTrue(myWaves.sineDict.get('isInit',{}))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 0 * (myPeriod / mySample))
        # Init with middle value, phase=180deg
        self.assertTrue(myWaves.sine_init(sample=2, period=1800, low=-20, high=20, init=0, posSlope=False))
        self.assertTrue(myWaves.sineDict.get('isInit',{}))
        self.assertEqual(myWaves.period_sec, myPeriod)
        self.assertEqual(myWaves.sample_sec, mySample)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('amp'), 20)
        self.assertEqual(myWaves.sineDict.get('wave',{}).get('ofs'), 0)
        self.assertEqual(myWaves.iterator, 1/2 * (myPeriod / mySample))
    #*****************************
    
    
    #*****************************
    def test_sine(self):
        # some preparation
        mySample = 2    # sample time in seconds, every two seconds a new sample point
        myPeriod = 1800 # period in seconds
        lowVal = 0
        highVal = 20
        ampVal = (highVal - lowVal) / 2
        # init sine
        myWaves = waves.waves()
        self.assertTrue(myWaves.sine_init(sample=mySample, period=myPeriod, low=lowVal, high=highVal, init=ampVal, posSlope=True))
        self.assertEqual(myWaves.iterator, 0 * (myPeriod / mySample))
        # check sine
        for i in range(0, int((myPeriod / mySample))-1):
            self.assertEqual(myWaves.iterator, i)   # iterator needs to incremented by one
            newVal = myWaves.sine()                 # update wave
            # check only in 90 degree grid to numeric resolution
            if ( i == int(0 * (myPeriod / mySample)) ):
                self.assertEqual(round(newVal.get('val'), 10), ampVal)                    # round to numeric noise, 10digits
                self.assertEqual(newVal.get('grad'), ampVal*2*math.pi*mySample/myPeriod)  # highest slew rate
            elif ( i == int(0.25 * (myPeriod / mySample)) ):
                self.assertEqual(newVal.get('val'), highVal)
                self.assertEqual(round(newVal.get('grad'), 10), float(0))   # round to numeric noise, 10digits
            elif ( i == int(0.5 * (myPeriod / mySample)) ):
                self.assertEqual(round(newVal.get('val'), 10), ampVal)                        # round to numeric noise, 10digits
                self.assertEqual(newVal.get('grad'), -ampVal*2*math.pi*mySample/myPeriod)     # highest slew rate
            elif ( i == int(0.75 * (myPeriod / mySample)) ):
                self.assertEqual(newVal.get('val'), lowVal)
                self.assertEqual(round(newVal.get('grad'), 10), float(0))   # round to numeric noise, 10digits
    #*****************************


    #*****************************
    def test_trapezoid(self):
        """
        @note:  tests sine init function
        """       
        # create test class
        dut = waves.waves()
        # unexpected argument
        with self.assertRaises(ValueError) as cm:
            dut.trapezoid(foo=5)
        self.assertEqual(str(cm.exception), "Unkown optional argument 'foo'")
        # exception: rise/fall time larger then period
        with self.assertRaises(ValueError) as cm:
            dut.trapezoid(tp=5, tr=4, tf=2)
        self.assertEqual(str(cm.exception), "Rise + Fall time is larger then period, minimal period length is 6s")
        # exception: unambiguously waveform
        with self.assertRaises(ValueError) as cm:
            dut.trapezoid()
        self.assertEqual(str(cm.exception), "Provided arguments does not unambiguously describe the waveform")
        # check init
        mySample = 2    # sample time in seconds, every two seconds a new sample point
        myPeriod = 1800 # period in seconds
        lowVal = -20
        highVal = 20
        initVal = 0
        (iter, wave) = dut.trapezoid(ts=mySample, tp=myPeriod, lowVal=lowVal, highVal=highVal, dutyCycle=0.5, initVal=initVal, tr=myPeriod/4, tf=myPeriod/4)
        self.assertEqual(iter, round(1/8*(myPeriod/mySample)))
        self.assertEqual(wave['part']['rise']['start'], 0)
        self.assertEqual(wave['part']['rise']['stop'], round(1/4*(myPeriod/mySample))-1)
        self.assertEqual(wave['part']['high']['start'], round(1/4*(myPeriod/mySample)))
        self.assertEqual(wave['part']['high']['stop'], round(2/4*(myPeriod/mySample))-1)
        self.assertEqual(wave['part']['fall']['start'], round(2/4*(myPeriod/mySample)))
        self.assertEqual(wave['part']['fall']['stop'], round(3/4*(myPeriod/mySample))-1)
        self.assertEqual(wave['part']['low']['start'], round(3/4*(myPeriod/mySample)))
        self.assertEqual(wave['part']['low']['stop'], round(4/4*(myPeriod/mySample))-1)
        
            
    #*****************************
    
    
    
    
    

        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
