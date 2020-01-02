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
    def test_sine_init(self):
        """
        @note:  tests sine init function
        """
        # some preparation
        sample = 2      # sample time in seconds, every two seconds a new sample point
        period = 1800   # period in seconds
        lowVal = -20
        highVal = 20
        # create class
        dut = waves.waves()
        # Init with max amp, phase=90deg
        (iter, wave) = dut.sine(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, initVal=20, pSlope=True)
        self.assertEqual(wave['x']['tp'], period)
        self.assertEqual(wave['x']['ts'], sample)
        self.assertEqual(wave['y']['amp'], 20)
        self.assertEqual(wave['y']['ofs'], 0)
        self.assertEqual(iter, 1/4 * (period / sample))
        # Init with min amp, phase=270deg
        (iter, wave) = dut.sine(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, initVal=-20, pSlope=True)
        self.assertEqual(wave['x']['tp'], period)
        self.assertEqual(wave['x']['ts'], sample)
        self.assertEqual(wave['y']['amp'], 20)
        self.assertEqual(wave['y']['ofs'], 0)
        self.assertEqual(iter, 3/4 * (period / sample))
        # Init with middle value, phase=0deg
        (iter, wave) = dut.sine(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, initVal=0, pSlope=True)
        self.assertEqual(wave['x']['tp'], period)
        self.assertEqual(wave['x']['ts'], sample)
        self.assertEqual(wave['y']['amp'], 20)
        self.assertEqual(wave['y']['ofs'], 0)
        self.assertEqual(iter, 0 * (period / sample))
        # Init with middle value, phase=180deg
        (iter, wave) = dut.sine(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, initVal=0, pSlope=False)
        self.assertEqual(wave['x']['tp'], period)
        self.assertEqual(wave['x']['ts'], sample)
        self.assertEqual(wave['y']['amp'], 20)
        self.assertEqual(wave['y']['ofs'], 0)
        self.assertEqual(iter, 1/2 * (period / sample))
    #*****************************
    
    
    #*****************************
    def test_sine(self):
        # some preparation
        sample = 2      # sample time in seconds, every two seconds a new sample point
        period = 1800   # period in seconds
        lowVal = 0
        highVal = 20
        ampVal = (highVal - lowVal) / 2
        ofsVal = ampVal + lowVal
        # init sine
        dut = waves.waves()
        (iter, wave) = dut.sine(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, initVal=ampVal, pSlope=True)
        self.assertDictEqual(wave, {'x': {'ts': sample, 'tp': period, 'n': period/sample}, 'y': {'ofs': ofsVal, 'amp': ampVal}})
        self.assertEqual(iter, 0 * (period / sample))
        # check sine
        for i in range(0, int((period / sample))-1):
            self.assertEqual(iter, i)                       # iterator needs to incremented by one
            (iter, newVal) = dut.sine(descr=(iter,wave))    # update wave
            # check only in 90 degree grid to numeric resolution
            if ( i == int(0 * (period / sample)) ):
                self.assertEqual(round(newVal['val'], 10), ampVal)                                      # round to numeric noise, 10digits
                self.assertEqual(round(newVal['grad'], 10), round(ampVal*2*math.pi*sample/period, 10))  # highest slew rate
            elif ( i == int(0.25 * (period / sample)) ):
                self.assertEqual(round(newVal['val'], 10), highVal)
                self.assertEqual(round(newVal['grad'], 10), float(0))   # round to numeric noise, 10digits
            elif ( i == int(0.5 * (period / sample)) ):
                self.assertEqual(round(newVal['val'], 10), ampVal)                                          # round to numeric noise, 10digits
                self.assertEqual(round(newVal['grad'], 10), round(-ampVal*2*math.pi*sample/period, 10))     # highest slew rate
            elif ( i == int(0.75 * (period / sample)) ):
                self.assertEqual(round(newVal['val'], 10), lowVal)
                self.assertEqual(round(newVal['grad'], 10), float(0))   # round to numeric noise, 10digits
    #*****************************


    #*****************************
    def test_trapezoid_exception(self):
        """
        @note:  tests exception handling of trapezoid function
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
    #*****************************
    
    
    #*****************************
    def test_trapezoid_init(self):
        """
        @note:  tests exception handling of trapezoid function
        """       
        # create test class
        dut = waves.waves()
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
