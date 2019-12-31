# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          waves.py
@date:          2019-08-24
@version:       0.1.0

@note           calculation formulas for waveform
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
        @note:          intializises class
        """
        self.wp = {}                        # wave parameters
        self.wp['wave'] = "sine"            # default waveform
        self.wp['ts'] = 1                   # sample time in sec
        self.wp['tp'] = 3600                # periode time in sec
        self.wp['lowval'] = 0               # low value
        self.wp['highval'] = 1              # high value
        self.wp['initval'] = float("nan")   # low value
        
        
        self.sample_sec = 1                     # sample time is 1sec
        self.period_sec = 3600                  # periode in sec
        self.iterator = 0                       # waveform iterator
        self.verbose = 0                        # suppress messages
        self.trapezoidDict = {}                 # storage element for trapezoid function
        self.trapezoidDict['isInit'] = False    # set uninitialized
        self.sineDict = {}                      # 
        self.sineDict['isInit'] = False         #
    #*****************************
    
    
    #*****************************
    def divide(self, dividend, divisor):
        """
        @note:  calculates quotient and return nan in case of zero devision
        
        @param dividend:    input number which should divided
        @param divisor:     divides divident
        
        @return:            quotient of division
        """
        try:
            return float(dividend/divisor)
        except ZeroDivisionError:
            if ( dividend >= 0 ):
                return float('inf')
            else:
                return float('-inf')
    #*****************************
    
    
    #*****************************
    def clear_init(self):
        """
        @note:      clear init flags
        
        @return:    successful
        """
        # clear flags
        self.trapezoidDict['isInit'] = False
        self.sineDict['isInit'] = False
        # graceful end
        return True
    #*****************************


    #*****************************
    def set(self, **kwargs):
        """
        @note:      clear init flags
        
        @return:    successful
        """
        # iterate and autocomplete
        for key, value in kwargs.items(): 
            print ("%s == %s" %(key, value))
        
        
        pass
    
    
    
    #*****************************
    def next(self):
        """
        @note:      go on discrete time step forward
        
        @return:    dict with new temperature and gradient
        """        
        
        pass




    #*****************************
    def sine_init(self, sample=None, period=None, low=None, high=None, init=None, posSlope=True):
        """
        @note:              initializes sine waveform
        
        @param sample:      Sample/Update time of waveform  in seconds
        @param period:      Period time of waveform in seconds
        @param low:         minimal value
        @param high:        maximal value
        @param init:        initialializes sine with value
        @type init:         None: no init; number: adjust sine phase to meet set value; nan: start at zero in waveform
        @param posSlope:    selects positive/negativ slope side of sine, only evaluated in init
        @type posSlope:     True: sine starts with increasing his values; False: sine start with decreasing his values 
        
        @return:            state
        @type               True: successful; False: failed
        """
        # clear init flags
        if ( True != self.clear_init() ):
            if ( 0 != self.verbose ):
                print("Error: Clear Flags")
            return False        
        # check for mandatory args
        if ( None == sample or None == period or None == low or None == high ):
            if ( 0 != self.verbose ):
                print("Error: Missing Argument")
            return False        
        # update waveform settings
        self.sample_sec = sample
        self.period_sec = period
        self.period_n = round(self.period_sec/self.sample_sec)      # number of steps for full periode
        # calc offset amplitude
        waveform = {}
        waveform['amp'] = (high - low) / 2
        waveform['ofs'] = waveform['amp'] + low 
        # init sine?
        if ( None != init ):
            # sine allign to temp desiered?
            if ( math.isnan(init) ): 
                self.iterator = 0
            else:
                # ensure inside temp range
                init = min(init, waveform['ofs'] + waveform['amp'])     # apply upper fence
                init = max(init, waveform['ofs'] - waveform['amp'])     # applay lower fence
                # init wave iterator
                self.iterator = (self.period_sec/(2*math.pi*self.sample_sec)) * math.asin((init-waveform['ofs'])/(waveform['amp']))
                self.iterator = round(self.iterator)
                # shift to first period
                if ( self.iterator < 0 ):
                    self.iterator  += self.period_n
                if ( self.iterator > self.period_n-1 ):
                    self.iterator  -= self.period_n
                # change slew direction
                if ( True == posSlope ):
                    if ( 0.25*self.period_n < self.iterator <= 0.5*self.period_n ):    # shift to [0*n, 0.25*n]
                        self.iterator = 0.25*self.period_n - self.iterator
                    elif ( 0.5*self.period_n < self.iterator <= 0.75*self.period_n ):  # shift to [0.75*n, n]
                        self.iterator = 0.75*self.period_n + (0.75*self.period_n-self.iterator)
                else:
                    if ( 0 <= self.iterator <= 0.25*self.period_n):        # shift to [0.25*n, 0.5*n]
                        self.iterator = 0.25*self.period_n + (0.25*self.period_n - self.iterator)
                    elif ( 0.75*self.period_n < self.iterator <= self.period_n):       # shift to [0.5*n, 0.75*n]
                        self.iterator = 0.75*self.period_n - (self.iterator - 0.75*self.period_n)
        else:
            if ( 0 != self.verbose ):
                print("Error: Init function with init arg called")
            return False
        # store in common storage element
        self.sineDict['wave'] = waveform        
        # wave is initialized
        self.sineDict['isInit'] = True
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def sine(self):
        """
        @note:              calculates sine waveform
        
        @return new:        dictionary with new setting
        @rtype new:         val: new value; grad: gradient of waveform
        """
        # check for init
        if (True != self.sineDict.get('isInit')):
            if ( 0 != self.verbose ):
                print("Error: 'trapezoid' function unintializied, call 'trapezoid_init'")
            return False
        # create dict
        new = {}
        # calculate discrete sine
        new['val'] = self.sineDict.get('wave',{}).get('ofs') + self.sineDict.get('wave',{}).get('amp')*(math.sin(2*math.pi*((self.iterator)*self.sample_sec/self.period_sec)))
        # calc gradient, derived discrete sine
        new['grad'] = self.sineDict.get('wave',{}).get('amp')*(2*math.pi*self.sample_sec/self.period_sec)*(math.cos(2*math.pi*((self.iterator)*self.sample_sec/self.period_sec)))
        # prepare for next calc
        self.iterator += 1
        # jump to sine start
        if ( self.iterator > self.period_n-1 ):
            self.iterator -= self.period_n
        # graceful end
        return new
    #*****************************
    
    
    #*****************************
    def trapezoid(self, descr=None, ts=1, tp=3600, lowVal=0, highVal=1, **kwargs):
        """
        @note:              generates discrete trapezoid waveform
        
        @param descr:       waveform descriptor, generated by this function in init phase
        @param ts:          Sample/Update time of waveform  in seconds
        @param tp:          Period time of waveform in seconds
        @param lowVal:      minimal value of trapezoid
        @param highVal:     maximal value of trapezoid
        @param tr:          rise time in sec from min to max
        @param tf:          fall time in sec from max to min
        @param duty:        ratio from max-to-min except the transition times (rise/fall)
        @param posSlope:    selects positive/negativ slope side of sine, only evaluated in init
        @type posSlope:     True: sine starts with increasing his values; False: sine start with decreasing his values
        
        @return:            init succesful
        """
        # init phase
        if ( None == descr ):
            # optarg defaults
            optarg = {}
            optarg['pSlope'] = True             # waveform increses with vals
            optarg['tf'] = 0                    # fall time, time from highVal to lowVal
            optarg['tr'] = 0                    # rise time
            optarg['initVal'] = float("nan")    # init iterator for this start value
            optarg['dutyCycle'] = float("nan")  # ratio high/low val time
            # check optional arguments
            for key, value in kwargs.items(): 
                if ( key in optarg ):
                    optarg[key] = value
                else:
                    raise ValueError("Unkown optional argument '" + key + "'")
            # w/ rise/fall time does wave exist
            if ( 0 > (tp - optarg['tf'] - optarg['tr']) ):
                raise ValueError("Rise + Fall time is larger then period, minimal period length is " + str(optarg['tf']+optarg['tr']) +"s")
            # define length of wave in discrete steps
            time = {}                   # waveforms time behaviour
            time['ts'] = ts             # sample rate
            time['tp'] = tp             # periode
            time['n'] = round(tp/ts)    # number of steps for full periode
            # determine discrte time steps of waveform
            # duty cycle is given
            if ( False == math.isnan(optarg['dutyCycle']) ):
                # calculate dicrete time steps
                step_rise_n = round(optarg['tr']/ts)                                            # number of steps for rise
                step_fall_n = round(optarg['tf']/ts)                                            # number of steps for fall
                step_high_n = round((time['n']-step_rise_n-step_fall_n)*optarg['dutyCycle'])    # number of steps for high
                step_low_n = time['n']-step_rise_n-step_fall_n-step_high_n                      # number of steps for low                
            # next wave style
            
            # not unambiguously described
            else:
                raise ValueError("Provided arguments does not unambiguously describe the waveform")
            # build piecewise continuous function
            # {'min'}: iter_min, {'max'}: iter_max, {'grad'}: gradient, {'start'}: start value for this segment
            part = {}
            part['rise'] = {'start': 0,                      'stop': step_rise_n-1,                        'grad': self.divide(highVal-lowVal, step_rise_n), 'val': lowVal}     # rise part
            part['high'] = {'start': part['rise']['stop']+1, 'stop': part['rise']['stop']+1+step_high_n-1, 'grad': 0,                                        'val': highVal}    # high part
            part['fall'] = {'start': part['high']['stop']+1, 'stop': part['high']['stop']+1+step_fall_n-1, 'grad': self.divide(lowVal-highVal, step_fall_n), 'val': highVal}    # fall part
            part['low']  = {'start': part['fall']['stop']+1, 'stop': part['fall']['stop']+1+step_low_n-1,  'grad': 0,                                        'val': lowVal}     # low part
            # find start value of iterator
            if ( math.isnan(optarg['initVal']) ): 
                iterator = 0
            else:
                # ensure inside temp range
                initVal = min(optarg['initVal'], highVal)   # apply upper fence
                initVal = max(initVal, lowVal)              # apply lower fence
                # init wave iterator
                if ( (True == optarg['pSlope']) and (0 != step_rise_n) ):       # waveform rises smooth
                    iterator = part['rise']['start'] + round((initVal-lowVal)/(abs(highVal-lowVal)/step_rise_n))
                elif ( (False == optarg['pSlope']) and (0 != step_fall_n) ):    # waveform falls smooth
                    iterator = part['fall']['start'] + round((highVal-initVal)/(abs(highVal-lowVal)/step_fall_n))
                else:                                                           # brick wall
                    iterator = 0
            # build final and return
            wave = {}
            wave['time'] = time
            wave['part'] = part
            return (iterator, wave)
        # calculate next step
        else:
            # disassemble descriptor
            iterator, wave = descr
            # calc waveform
            new = {}
            for foo, part in wave['part'].items():
                # match part of waveform
                if ( part['start'] <= iterator <= part['stop'] ):
                    new['val'] = part['val'] + part['grad'] * (iterator-part['start'])  # new value value
                    new['grad'] = part['grad'] / wave['time']['ts']                     # gradient per sec
            # inc wave iterator, prepare for next calc
            iterator += 1
            # jump to start
            if ( iterator > wave['time']['tp']-1 ):
                iterator -= wave['time']['tp']
            # assign to release struct
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
    