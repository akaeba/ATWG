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
        @note   set-ups test
        """
    #*****************************
    
    
    #*****************************
    def test_divide(self):
        """
        @note   tests zero divide divider function
        """
        myWaves = waves.waves()     # create class
        self.assertEqual(myWaves.divide(dividend=1, divisor=2), 0.5)                # normal devision
        self.assertTrue(float('inf') == myWaves.divide(dividend=1, divisor=0))      # check divide by zero
        self.assertTrue(float('-inf') == myWaves.divide(dividend=-1, divisor=0))    #
        self.assertTrue(math.isnan(myWaves.divide(dividend=0, divisor=0)))          #
    #*****************************
    
    
    #*****************************
    def test_sine_exception(self):
        """
        @note   tests sine init functionality
        """
        # create test class
        dut = waves.waves()
        # unexpected argument
        with self.assertRaises(ValueError) as cm:
            dut.sine(foo=5)
        self.assertEqual(str(cm.exception), "Unkown optional argument 'foo'")
    #*****************************
    
    
    
    #*****************************
    def test_sine_init(self):
        """
        @note   tests sine init functionality
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
        """
        @note   tests sine function
        """ 
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
        @note   tests exception handling of trapezoid function
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
        @note   tests trapezoid init functionality
        """       
        # init values
        dut = waves.waves()
        sample = 2    # sample time in seconds, every two seconds a new sample point
        period = 1800 # period in seconds
        lowVal = -20
        highVal = 20
        initVal = 0
        # init & check
        (iter, wave) = dut.trapezoid(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, dutyCycle=0.5, initVal=initVal, tr=period/4, tf=period/4)
        self.assertEqual(iter, round(1/8*(period/sample)))
        self.assertEqual(wave['y']['rise']['start'], 0)
        self.assertEqual(wave['y']['rise']['stop'], round(1/4*(period/sample))-1)
        self.assertEqual(wave['y']['high']['start'], round(1/4*(period/sample)))
        self.assertEqual(wave['y']['high']['stop'], round(2/4*(period/sample))-1)
        self.assertEqual(wave['y']['fall']['start'], round(2/4*(period/sample)))
        self.assertEqual(wave['y']['fall']['stop'], round(3/4*(period/sample))-1)
        self.assertEqual(wave['y']['low']['start'], round(3/4*(period/sample)))
        self.assertEqual(wave['y']['low']['stop'], round(4/4*(period/sample))-1)
    #*****************************
    
    
    #*****************************
    def test_trapezoid(self):
        """
        @note   tests trapezoid function
        """  
        # init values
        dut = waves.waves()        
        sample = 2    # sample time in seconds, every two seconds a new sample point
        period = 1800 # period in seconds
        lowVal = -20
        highVal = 20
        (iter, wave) = dut.trapezoid(ts=sample, tp=period, lowVal=lowVal, highVal=highVal, dutyCycle=0.5, tr=(highVal-lowVal)*sample, tf=(highVal-lowVal)*sample)
        # check waveform init
        self.assertEqual(iter, 0)
        self.assertEqual(wave['y']['rise']['start'], 0)
        self.assertEqual(wave['y']['rise']['stop'], 39)
        self.assertEqual(wave['y']['high']['start'], 40)
        self.assertEqual(wave['y']['high']['stop'], 449)
        self.assertEqual(wave['y']['fall']['start'], 450)
        self.assertEqual(wave['y']['fall']['stop'], 489)
        self.assertEqual(wave['y']['low']['start'], 490)
        self.assertEqual(wave['y']['low']['stop'], 899)
        # calculate full period
        for i in range(0, int((period / sample))-1):
            self.assertEqual(iter, i)                           # iterator needs to incremented by one
            (iter, newVal) = dut.trapezoid(descr=(iter,wave))   # update wave            
            if ( 0 <= i <= 39 ):
                self.assertEqual(newVal['grad'], 0.5)
                self.assertEqual(newVal['val'], lowVal+i)
            elif ( 40 <= i <= 449 ):
                self.assertEqual(newVal['grad'], 0)
                self.assertEqual(newVal['val'], highVal)
            elif ( 450 <= i <= 489 ):
                self.assertEqual(newVal['grad'], -0.5)
                self.assertEqual(newVal['val'], highVal-(i-450))
            elif ( 490 <= i <= 899 ):
                self.assertEqual(newVal['grad'], 0)
                self.assertEqual(newVal['val'], lowVal)
    #*****************************
    
    
    #*****************************
    def test_set_exception(self):
        """
        @note   tests exception handling of set function
        """  
        # init values
        dut = waves.waves()      
        # unsupported waveform
        with self.assertRaises(ValueError) as cm:
            dut.set(wave="foo")
        self.assertEqual(str(cm.exception), "Unsupported waveform 'foo' requested")
        # too less args
        with self.assertRaises(ValueError) as cm:
            dut.set(wave="trapezoid")
        self.assertEqual(str(cm.exception), "Provided arguments does not unambiguously describe the waveform")
    #*****************************
    
    
    #*****************************
    def test_set(self):
        """
        @note   tests set function
        """  
        # init values
        dut = waves.waves()
        sample = 1    # sample time in seconds, every two seconds a new sample point
        period = 1800 # period in seconds
        lowVal = -20
        highVal = 20
        # init wave & check
        self.assertTrue(dut.set(wave="sine", ts=sample, tp=period, lowVal=lowVal, highVal=highVal))
        self.assertDictEqual(dut.waveDescr, {'x': {'ts': sample, 'tp': period, 'n': period/sample}, 'y': {'ofs': (highVal+lowVal)/2, 'amp': (highVal-lowVal)/2}})
        self.assertTrue("sine" == dut.usedWaveform)
    #*****************************


    #*****************************
    def test_next_exception(self):
        """
        @note   tests next function exception handling
        """  
        # init values
        dut = waves.waves()
        # unsupported waveform
        with self.assertRaises(ValueError) as cm:
            dut.next()
        self.assertEqual(str(cm.exception), "Uninitialized waveform")
    #*****************************
    
    
    #*****************************
    def test_next(self):
        """
        @note   tests next function
        """  
        # init values
        dut = waves.waves()    
        sample = 1    # sample time in seconds, every two seconds a new sample point
        period = 1800 # period in seconds
        lowVal = -20
        highVal = 20
        dutyCycle = 0.5
        # init wave
        self.assertTrue(dut.set(wave="trapezoid", ts=sample, tp=period, lowVal=lowVal, highVal=highVal, dutyCycle=dutyCycle))
        # iterate and check
        cnt = 0
        for i in range(0, 2*int((period / sample))-1):
            # calc next step
            val = dut.next()
            # check waveform
            if ( 0 <= cnt <= 899 ):
                self.assertEqual(val['grad'], 0)
                self.assertEqual(val['val'], highVal)
            elif ( 900 <= cnt <= 1799 ):
                self.assertEqual(val['grad'], 0)
                self.assertEqual(val['val'], lowVal)
            # help counter for segment diviation
            cnt += 1
            if ( cnt > int((period / sample))-1 ):
                cnt = 0
            # check iterator
            self.assertEqual(dut.iterator, cnt)
        #*****************************

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
