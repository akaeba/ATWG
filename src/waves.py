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
            return float("nan")
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
    def trapezoid_init(self, sample=None, period=None, low=None, high=None, init=None, rise=0, fall=0, dutyMax=float(0.5), posSlope=True):
        """
        @note:              initializes trapezoid waveform
        
        @param sample:      Sample/Update time of waveform  in seconds
        @param period:      Period time of waveform in seconds
        @param low:         minimal value of trapezoid
        @param high:        maximal value of trapezoid
        @param rise:        rise time in sec from min to max
        @param fall:        fall time in sec from max to min
        @param dutyMax:     ratio from max-to-min except the transition times (rise/fall)
        @param init:        initialializes temperature wave form
        @type init:         None: no init, calc next setting temperature; number: adjust to set temperature; nan: start at zero in waveform
        @param posSlope:    selects positive/negativ slope side of sine, only evaluated in init
        @type posSlope:     True: sine starts with increasing his values; False: sine start with decreasing his values
        
        @return:            init succesful
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
        # check for periode length
        if ( 0 > self.period_sec - rise - fall ):
            if ( 0 != self.verbose ):
                print("Error: Rise/Fall time to large for period length, minimal period length is " + str(rise+fall) +"s")
            return False
        # update waveform settings
        self.sample_sec = sample
        self.period_sec = period
        self.period_n = round(self.period_sec/self.sample_sec)      # number of steps for full periode
        # calc number of cycles
        step_rise_n = round(rise/self.sample_sec)                               # number of steps for rise
        step_fall_n = round(fall/self.sample_sec)                               # number of n steps for fall
        step_high_n = round((self.period_n-step_rise_n-step_fall_n)*dutyMax)    # number of steps for high
        step_low_n = self.period_n-step_rise_n-step_fall_n-step_high_n          # number of steps for low
        # define trapezoid wave
        # {'min'}: iter_min, {'max'}: iter_max, {'grad'}: gradient, {'start'}: start temperatur for this segment
        waveform = {}
        waveform['rise'] = {'min': 0, 'max': step_rise_n-1, 'grad': self.divide(high-low, step_rise_n), 'start': low};                                                                              # rise part
        waveform['high'] = {'min': waveform.get('rise',{}).get('max')+1, 'max': waveform.get('rise',{}).get('max')+1+step_high_n-1, 'grad': 0, 'start': high}                                       # high part
        waveform['fall'] = {'min': waveform.get('high',{}).get('max')+1, 'max': waveform.get('high',{}).get('max')+1+step_fall_n-1, 'grad':  self.divide(low-high, step_fall_n), 'start': high}     # fall part
        waveform['low']  = {'min': waveform.get('fall',{}).get('max')+1, 'max': waveform.get('fall',{}).get('max')+1+step_low_n-1, 'grad': 0, 'start': low}                                         # low part
        # init iterator
        if ( None != init ):
            if ( math.isnan(init) ): 
                self.iterator = 0
            else:
                # ensure inside temp range
                init = min(init, high)  # apply upper fence
                init = max(init, low)   # applay lower fence
                # init wave iterator
                if ( (True == posSlope) and (0 != step_rise_n) ):       # waveform rises smooth
                    self.iterator = waveform.get('rise',{}).get('min') + round((init-low)/(abs(high-low)/step_rise_n))
                elif ( (False == posSlope) and (0 != step_fall_n) ):    # waveform falls smooth
                    self.iterator = waveform.get('fall',{}).get('min') + round((high-init)/(abs(high-low)/step_fall_n))
                else:                                                   # brick wall
                    self.iterator = 0
        else:
            if ( 0 != self.verbose ):
                print("Error: Init function with init arg called")
            return False
        # store in common storage element
        self.trapezoidDict['wave'] = waveform
        # wave is initialized
        self.trapezoidDict['isInit'] = True
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def trapezoid(self):
        """
        @note:              calculates trapezoid waveform
        
        @return new:        dictionary with new setting
        @rtype new:         val: new value; grad: gradient of waveform
        """
        # check for init
        if (True != self.trapezoidDict.get('isInit')):
            if ( 0 != self.verbose ):
                print("Error: 'trapezoid' function unintializied, call 'trapezoid_init'")
            return False
        # calc waveform
        new = {}
        for part, wave in self.trapezoidDict.get('wave',{}).items():
            # match part of waveform
            if ( wave.get('min') <= self.iterator <= wave.get('max') ):
                new['val'] = wave.get('start') + wave.get('grad') * (self.iterator-wave.get('min'))
                new['grad'] = wave.get('grad')
        # inc wave iterator, prepare for next calc
        self.iterator += 1
        # jump to start
        if ( self.iterator > self.period_n-1 ):
            self.iterator -= self.period_n
        # assign to release struct
        return new
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
    