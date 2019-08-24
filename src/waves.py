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

        @return:        boolean
        """
        self.sample_sec = 1     # sample time is 1sec
        self.period_sec = 3600  # periode in sec
        self.iterator = 0       # waveform iterator
    #*****************************
    
    
    #*****************************
    def configure(self, sample=1, period=3600):
        """
        @note:          configures class
        
        @param sample:  Sample/Update time of waveform  in seconds
        @param period:  Period time of waveform in seconds
        
        @return:        boolean
        """
        self.sample_sec = sample
        self.period_sec = period
        return True                 # all done
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
    def sine(self, amp=None, ofs=None, init=None, posSlope=True):
        """
        @note:              calculates sine waveform
        
        @param amp:         amplitude of sine
        @param ofs:         offset of sine
        @param init:        initialializes temperature wave form
        @type init:         None: no init, calc next setting temperature; number: adjust to set temperature; nan: start at zero in waveform
        @param posSlope:    selects positive/negativ slope side of sine, only evaluated in init
        @type posSlope:     True: sine starts with increasing his values; False: sine start with decreasing his values
        
        @return new:        dictionary with new setting
        @rtype new:         val: new value; grad: gradient of waveform
        """
        # preparation
        n = round(self.period_sec/self.sample_sec)    # number of steps for full periode
        new = {}                                            # dictionary with calc result
        # check for args
        if ( None == amp or None == ofs ):
            return False
        # init sine?
        if ( None != init ):
            # sine allign to temp desiered?
            if ( math.isnan(init) ): 
                self.iterator = 0
            else:
                # ensure inside temp range
                init = min(init, ofs + amp)     # apply upper fence
                init = max(init, ofs - amp)     # applay lower fence
                # init wave iterator
                self.iterator = (self.period_sec/(2*math.pi*self.sample_sec)) * math.asin((init-ofs)/(amp))
                self.iterator = round(self.iterator)
                # shift to first period
                if ( self.iterator < 0 ):
                    self.iterator  += n
                if ( self.iterator > n-1 ):
                    self.iterator  -= n
                # change slew direction
                if ( True == posSlope ):
                    if ( 0.25*n < self.iterator <= 0.5*n ):    # shift to [0*n, 0.25*n]
                        self.iterator = 0.25*n - self.iterator
                    elif ( 0.5*n < self.iterator <= 0.75*n ):  # shift to [0.75*n, n]
                        self.iterator = 0.75*n + (0.75*n-self.iterator)
                else:
                    if ( 0 <= self.iterator <= 0.25*n):        # shift to [0.25*n, 0.5*n]
                        self.iterator = 0.25*n + (0.25*n - self.iterator)
                    elif ( 0.75*n < self.iterator <= n):       # shift to [0.5*n, 0.75*n]
                        self.iterator = 0.75*n - (self.iterator - 0.75*n)
                # enw w/o any set temp - it's init part
                return True
        # calculate discrete sine
        new['val'] = ofs + amp*(math.sin(2*math.pi*((self.iterator)*self.sample_sec/self.period_sec)))
        # calc gradient, derived discrete sine
        new['grad'] = amp*(2*math.pi*self.sample_sec/self.period_sec)*(math.cos(2*math.pi*((self.iterator)*self.sample_sec/self.period_sec)))
        # prepare for next calc
        self.iterator += 1
        # jump to sine start
        if ( self.iterator > n-1 ):
            self.iterator -= n
        # graceful end
        return new
    #*****************************
    
    
    #*****************************
    def trapezoid(self, low=None, high=None, init=None, rise=0, fall=0, dutyMax=float(0.5), posSlope=True):
        """
        @note:              calculates trapezoid waveform
        
        @param low:         minimal value of trapezoid
        @param high:        maximal value of trapezoid
        @param rise:        rise time in sec from min to max
        @param fall:        fall time in sec from max to min
        @param dutyMax:     ratio from max-to-min except the transition times (rise/fall)
        @param init:        initialializes temperature wave form
        @type init:         None: no init, calc next setting temperature; number: adjust to set temperature; nan: start at zero in waveform
        @param posSlope:    selects positive/negativ slope side of sine, only evaluated in init
        @type posSlope:     True: sine starts with increasing his values; False: sine start with decreasing his values
        
        @return new:        dictionary with new setting
        @rtype new:         val: new value; grad: gradient of waveform
        """
        # check for mandatory args
        if ( None == low or None == high ):
            return False
        # check for periode length
        if ( 0 > self.period_sec - rise - fall ):
            print("Error: Rise/Fall time to large for period length, minimal period length is " + str(rise+fall) +"s")
            return False
        # calc number of cycles
        n = round(self.period_sec/self.sample_sec)                  # number of steps for full periode
        step_rise_n = round(rise/self.sample_sec)                   # number of steps for rise
        step_fall_n = round(fall/self.sample_sec)                   # number of n steps for fall
        step_high_n = round((n-step_rise_n-step_fall_n)*dutyMax)    # number of steps for high
        step_low_n = n-step_rise_n-step_fall_n-step_high_n          # number of steps for low
        # define trapezoid wave
        # {'min'}: iter_min, {'max'}: iter_max, {'grad'}: gradient
        waveform = {}
        waveform['rise'] = {'min': 0, 'max': step_rise_n-1, 'grad': self.divide(high-low, step_rise_n), 'start': low};                                                                              # rise part
        waveform['high'] = {'min': waveform.get('rise',{}).get('max')+1, 'max': waveform.get('rise',{}).get('max')+1+step_high_n-1, 'grad': 0, 'start': high}                                       # high part
        waveform['fall'] = {'min': waveform.get('high',{}).get('max')+1, 'max': waveform.get('high',{}).get('max')+1+step_fall_n-1, 'grad':  self.divide(low-high, step_fall_n), 'start': high}     # fall part
        waveform['low']  = {'min': waveform.get('fall',{}).get('max')+1, 'max': waveform.get('fall',{}).get('max')+1+step_low_n-1, 'grad': 0, 'start': low}                                         # low part
        # init?
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
                    return True
                elif ( (False == posSlope) and (0 != step_fall_n) ):    # waveform falls smooth
                    self.iterator = waveform.get('fall',{}).get('min') + round((high-init)/(abs(high-low)/step_fall_n))
                    return True
                else:                                                   # brick wall
                    self.iterator = 0
                    return True
        # calc waveform
        new = {} 
        for part in waveform:
            # match part of waveform
            if ( waveform.get(part,{}).get('min') <= self.iterator <= waveform.get(part,{}).get('max') ):
                new['val'] = waveform.get(part,{}).get('start') + waveform.get(part,{}).get('grad') * (self.iterator-waveform.get(part,{}).get('min'))
                new['grad'] = waveform.get(part,{}).get('grad')
        # inc wave iterator, prepare for next calc
        self.iterator += 1
        # jump to start
        if ( self.iterator > n-1 ):
            self.iterator -= n
        # assign to release struct
        return new
    #*****************************    
    
    
    
    
    



#------------------------------------------------------------------------------