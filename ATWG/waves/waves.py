# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          waves.py
@date:          2019-08-24

@note           calculates discrete waveforms
"""



#------------------------------------------------------------------------------
import math     # sine
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class waves:
    """
    @note:  class to create numeric waveforms
    """

    #*****************************
    def __init__(self):
        """
        @note:          initializes class
        """
        self.waveDescr = {} # descriptor of initializes waveform
        self.iterator = 0   # waveform iterator
        self.waveArgs = {}  # not initialized
    #*****************************


    #*****************************
    def divide(self, dividend, divisor):
        """
        @note   calculates quotient and return nan in case of zero devision

        @param dividend     input number which should divided
        @param divisor      divides dividend

        @return             quotient of division
        """
        try:
            return float(dividend/divisor)
        except ZeroDivisionError:
            if ( 0 < dividend ):
                return float('inf')
            elif ( 0 > dividend ):
                return float('-inf')
            else:
                return float('nan')
    #*****************************


    #*****************************
    def set(self, **kwargs):
        """
        @note       selects waveform, and initializes waveform with proper arguments

        @see        sine()
        @see        trapezoid()

        @return:    True
        """
        # prepare
        self.waveDescr = {}     # reset wave descriptor
        self.waveArgs = {}      # make invalid
        waveParam = {}          # for waveform construction
        # assign kwargs to dict
        for key, value in kwargs.items():
            # separate waveform description from waveform selection
            if ( key != "wave" ):
                waveParam[key] = value
            # assign to storage element
            self.waveArgs[key] = value
        # init waveform
        if ( "sine" == self.waveArgs['wave'] ):
            (self.iterator, self.waveDescr) = self.sine(**waveParam)        # sine
        elif ( "trapezoid" == self.waveArgs['wave'] ):
            (self.iterator, self.waveDescr) = self.trapezoid(**waveParam)   # trapezoid
        else:
            raise ValueError("Unsupported waveform '" + self.waveArgs['wave'] + "' requested")
        # normal end
        return True
    #*****************************


    #*****************************
    def next(self):
        """
        @note       go one discrete time step forward

        @return     dict with new temperature and gradient
        """
        # init
        newVal = {}
        # in case of non intinilaized waveform is waveArgs not avialable
        try:
            # dispatch
            if ( "sine" == self.waveArgs['wave'] ):
                (self.iterator, newVal) = self.sine(descr=(self.iterator,self.waveDescr))       # update
            elif ( "trapezoid" == self.waveArgs['wave'] ):
                (self.iterator, newVal) = self.trapezoid(descr=(self.iterator,self.waveDescr))  # update
            else:
                raise ValueError("Unsupported waveform")
        except:
            raise ValueError("Uninitialized waveform")
        # return new vals
        return newVal
    #*****************************


    #*****************************
    def sine(self, descr=None, **kwargs):
        """
        @note           initializes and calculates next value

        @param descr    Sample/Update time of waveform  in seconds
        @param ts       Sample/Update time of waveform in base time units (f.e. seconds)
        @param tp       Period time of waveform in base time units (f.e. seconds)
        @param lowVal   minimal value
        @param highVal  maximal value
        @param initVal  initializes sine with value
        @param pSlope   selects positive/negative slope side of sine, only evaluated in init
        @return         wave descriptor or next value tupple
        @see            test_sine_init, test_sine for usage
        """
        # init phase
        if ( None == descr ):
            # optarg defaults
            optarg = {}
            optarg['ts'] = 1                    # sampling time
            optarg['tp'] = 3600                 # period time in sampling time steps
            optarg['lowVal'] = 0                # low value of sine
            optarg['highVal'] = 1               # high value of sine
            optarg['initVal'] = float("nan")    # init iterator for this start value
            optarg['pSlope'] = True             # waveform increases with time
            # check optional arguments
            for key, value in kwargs.items():
                if ( key in optarg ):
                    optarg[key] = value
                else:
                    raise ValueError("Unknown optional argument '" + key + "'")
            # define length of wave in discrete steps
            x = {}                              # waveforms time behaviour
            x['ts'] = optarg['ts']              # sample rate
            x['tp'] = optarg['tp']              # periode
            x['n'] = round(x['tp']/x['ts'])     # number of steps for full periode
            # value base of waveform
            y = {}
            y['amp'] = (optarg['highVal'] - optarg['lowVal']) / 2   # sine amplitude
            y['ofs'] = (optarg['highVal'] + optarg['lowVal']) / 2   # sine offset
            # find start value of iterator
            if ( math.isnan(optarg['initVal']) ):
                iterator = 0
            else:
                # ensure inside temp range
                initVal = min(optarg['initVal'], optarg['highVal'])   # apply upper fence
                initVal = max(initVal, optarg['lowVal'])              # applay lower fence
                # init wave iterator
                iterator = (x['tp']/(2*math.pi*x['ts'])) * math.asin((initVal-y['ofs'])/y['amp'])
                iterator = round(iterator)
                # shift to first period
                if ( iterator < 0 ):
                    iterator  += x['n']
                if ( iterator > x['n']-1 ):
                    iterator  -= x['n']
                # change slew direction
                if ( True == optarg['pSlope'] ):
                    if ( 0.25*x['n'] < iterator <= 0.5*x['n'] ):        # shift to [0*n, 0.25*n]
                        iterator = 0.25*x['n'] - iterator
                    elif ( 0.5*x['n'] < self.iterator <= 0.75*x['n'] ): # shift to [0.75*n, n]
                        iterator = 0.75*x['n'] + (0.75*x['n']-iterator)
                else:
                    if ( 0 <= iterator <= 0.25*x['n']):                 # shift to [0.25*n, 0.5*n]
                        iterator = 0.25*x['n'] + (0.25*x['n'] - iterator)
                    elif ( 0.75*x['n'] < self.iterator <= x['n']):      # shift to [0.5*n, 0.75*n]
                        iterator = 0.75*x['n'] - (iterator - 0.75*x['n'])
            # build waveform
            wave = {}
            wave['x'] = x
            wave['y'] = y
            # return iterator and wave
            return (iterator, wave)
        # calculate next temp value
        else:
            # disassemble descriptor
            iterator, wave = descr
            # calculate next time step
            new = {}
            new['val'] = wave['y']['ofs'] + wave['y']['amp']*(math.sin(2*math.pi*((iterator)*(float(1)/wave['x']['n']))))                       # calculate discrete sine value for n
            new['grad'] = wave['y']['amp']*(2*math.pi*(float(1)/wave['x']['n']))*(math.cos(2*math.pi*((iterator)*(float(1)/wave['x']['n']))))   # calc gradient, derived discrete sine
            # prepare for next calc
            iterator += 1
            # jump to sine start
            if ( iterator > wave['x']['n']-1 ):
                iterator -= wave['x']['n']
            # assign to release tupple
            return (iterator, new)
    #*****************************


    #*****************************
    def trapezoid(self, descr=None, **kwargs):
        """
        @note               generates discrete trapezoid waveform

        @param descr        waveform descriptor, generated by this function in init phase
        @param ts           Sample/Update time of waveform  in seconds
        @param tp           Period time of waveform in seconds
        @param lowVal       minimal value of trapezoid
        @param highVal      maximal value of trapezoid
        @param tr           rise time in sec from min to max
        @param tf           fall time in sec from max to min
        @param dutyCycle    ratio from max-to-min except the transition times (rise/fall)
        @param pSlope       selects positive/negativ slope side of sine, only evaluated in init
        @param initVal      initializes sine with value
        @return             wave descriptor or next value tupple
        @rtype              
        @see                test_trapezoid_init, test_trapezoid for usage
        """
        # init phase
        if ( None == descr ):
            # optarg defaults
            optarg = {}
            optarg['ts'] = 1                    # sampling time
            optarg['tp'] = 3600                 # period time in sampling time steps
            optarg['lowVal'] = 0                # low value of sine
            optarg['highVal'] = 1               # high value of sine
            optarg['pSlope'] = True             # waveform increases with vals
            optarg['tf'] = 0                    # fall time, time from highVal to lowVal
            optarg['tr'] = 0                    # rise time
            optarg['initVal'] = float("nan")    # init iterator for this start value
            optarg['dutyCycle'] = float("nan")  # ratio high/low val time
            # check optional arguments
            for key, value in kwargs.items():
                if ( key in optarg ):
                    optarg[key] = value
                else:
                    raise ValueError("Unknown optional argument '" + key + "'")
            # w/ rise/fall time does wave exist
            if ( 0 > (optarg['tp'] - optarg['tf'] - optarg['tr']) ):
                raise ValueError("Rise + Fall time is larger then period, minimal period length is " + str(optarg['tf']+optarg['tr']) +"s")
            # define length of wave in discrete steps
            x = {}                                      # waveforms time behavior
            x['ts'] = optarg['ts']                      # sample rate
            x['tp'] = optarg['tp']                      # period
            x['n'] = round(optarg['tp']/optarg['ts'])   # number of steps for full period
            # determine discrete time steps of waveform
            # duty cycle is given
            if ( False == math.isnan(optarg['dutyCycle']) ):
                # calculate discrete time steps
                step_rise_n = round(optarg['tr']/x['ts'])                                   # number of steps for rise
                step_fall_n = round(optarg['tf']/x['ts'])                                   # number of steps for fall
                step_high_n = round((x['n']-step_rise_n-step_fall_n)*optarg['dutyCycle'])   # number of steps for high
                step_low_n = x['n']-step_rise_n-step_fall_n-step_high_n                     # number of steps for low
            # next wave style

            # not unambiguously described
            else:
                raise ValueError("Provided arguments does not unambiguously describe the waveform")
            # build piecewise continuous function
            # {'min'}: iter_min, {'max'}: iter_max, {'grad'}: gradient, {'start'}: start value for this segment
            y = {}
            y['rise'] = {'start': 0,                   'stop': step_rise_n-1,                     'grad': self.divide(optarg['highVal']-optarg['lowVal'], step_rise_n), 'val': optarg['lowVal']}     # rise part
            y['high'] = {'start': y['rise']['stop']+1, 'stop': y['rise']['stop']+1+step_high_n-1, 'grad': 0,                                                            'val': optarg['highVal']}    # high part
            y['fall'] = {'start': y['high']['stop']+1, 'stop': y['high']['stop']+1+step_fall_n-1, 'grad': self.divide(optarg['lowVal']-optarg['highVal'], step_fall_n), 'val': optarg['highVal']}    # fall part
            y['low']  = {'start': y['fall']['stop']+1, 'stop': y['fall']['stop']+1+step_low_n-1,  'grad': 0,                                                            'val': optarg['lowVal']}     # low part
            # find start value of iterator
            if ( math.isnan(optarg['initVal']) ):
                iterator = 0
            else:
                # ensure inside temp range
                initVal = min(optarg['initVal'], optarg['highVal'])     # apply upper fence
                initVal = max(initVal, optarg['lowVal'])                # apply lower fence
                # init wave iterator
                if ( (True == optarg['pSlope']) and (0 != step_rise_n) ):       # waveform rises smooth
                    iterator = y['rise']['start'] + round((initVal-optarg['lowVal'])/(abs(optarg['highVal']-optarg['lowVal'])/step_rise_n))
                elif ( (False == optarg['pSlope']) and (0 != step_fall_n) ):    # waveform falls smooth
                    iterator = y['fall']['start'] + round((optarg['highVal']-initVal)/(abs(optarg['highVal']-optarg['lowVal'])/step_fall_n))
                else:                                                           # brick wall
                    iterator = 0
            # build final and return
            wave = {}
            wave['x'] = x
            wave['y'] = y
            return (iterator, wave)
        # calculate next step
        else:
            # disassemble descriptor
            iterator, wave = descr
            # calc waveform
            new = {}
            for foo, y in wave['y'].items():
                # match part of waveform
                if ( y['start'] <= iterator <= y['stop'] ):
                    new['val'] = y['val'] + y['grad'] * (iterator-y['start'])   # new value value
                    new['grad'] = y['grad'] / wave['x']['ts']                   # gradient per sec
            # inc wave iterator, prepare for next calc
            iterator += 1
            # jump to start
            if ( iterator > wave['x']['n']-1 ):
                iterator -= wave['x']['n']
            # assign to release tupple
            return (iterator, new)
    #*****************************

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
if __name__ == '__main__':

    # create object
    myWave = waves()
    # check trapezoid function
    myWave.trapezoid_init(sample=1, period=3600, low=-10, high=30, rise=10, fall=20, init=23, posSlope=True)
    print(str(myWave.iterator))
    print(myWave.trapezoid())
    # check sine function
    myWave.sine_init(sample=1, period=3600, low=-10, high=30, init=23, posSlope=True)
    print(str(myWave.iterator))
    print(myWave.sine())
#------------------------------------------------------------------------------
