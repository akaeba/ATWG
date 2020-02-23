# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          ATWG.py
@date:          2020-01-04
@version:       0.1.0

@note           Arbitrary Temperature Waveform Generator
                  - directly started from command line
                  - run with 'python ./ATWG <myArgs>'

@see            https://docs.python.org/3/library/exceptions.html#exception-hierarchy

"""



#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import argparse   # argument parser
import time       # time
import math       # sine
import itertools  # spinning progress bar
import re         # regex, needed for number string separation

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "./")))   # add project root to lib search path   
import driver.espec.sh_641_drv as sh_641_drv                                            # Espec SH641 chamber driver
import driver.sim.sim_chamber as simdev                                                 # simulation device
import waves.waves as waves                                                             # Discrete waveform generator
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class ATWG:
    #*****************************
    def __init__(self):
        """
        Initialization
        """
        # config
        self.cfg_tsample_sec = 1                    # sample time is 1sec
        self.avlChambers = ["SIM", "ESPEC_SH641",]  # supported climate chambers
        # storing elements
        self.chamber = None     # class for chamber
        self.wave = None        # waveform
        self.clima = None       # storage element for last measured clima
        # time string conversion
        self.timeToSec = {'s': 1, 'sec': 1, 'm': 60, 'min': 60, 'h': 3600, 'hour': 3600, 'd': 86400, 'day': 86400}   # conversion dictory to seconds
        self.timeColSep = "d:h:m:s"                                                                                  # colon separated time string prototype
        
        
        # collected args
        self.arg_sel_chamber = float("nan")     # selected chambers
        self.arg_sel_waveform = float("nan")    # choosen waveform
        self.arg_itf = ""                       # communication interface
        self.arg_periode_sec = float("nan")     # waveform periode in seconds
        self.arg_tmin = float("nan")            # minimal temperature in function
        self.arg_tmax = float("nan")            # maximal temerpature in function
        # chamber set
        self.tset = {}                      # init dict
        self.tset['val'] = float("nan")     # set temp
        self.tset['grad'] = float("nan")    # gradient
        self.hset = float("nan")            # setted humidity
        # chamber meas
        self.tmeas = float("nan")           # measured temperature
        self.hmeas = float("nan")           # measured humidity
        # supported chamber classes
        self.espesShSu = sh_641_drv.especShSu()    # create class without constructor call
        # chamber measurement resolution
        self.num_temps_fracs = 1   # temperature measurement fracs
        # Progress Spinner
        # SRC: https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
    #*****************************
    
    
    #*****************************
    def parse_cli(self, argv):
        """
        @note           Parses Arguments from Command line
        @see            https://docs.python.org/3.3/library/argparse.html
        
        @rtype          dict
        @return         parsed cli arguments to setup chamber and waveform
        """
        # create object
        parser = argparse.ArgumentParser(description="Arbitrary Temperature Waveform Generator")    # create class
        # waveform
        parser.add_argument('--sine',       action='store_true', help="sine waveform")                          # selects used waveform
        parser.add_argument('--trapezoid',  action='store_true', help="trapezoid waveform")                     #
        parser.add_argument('--invert',     action='store_true', help="wave starts with negative slew rate")    # w/o flag starts wave with positive slew, if set with negative slew
        # waveform parameters
        parser.add_argument("--period",    nargs=1, default=["1h",],    help="Period duration of selected waveform")            # interface
        parser.add_argument("--minTemp",   nargs=1, default=None,       help="minimal temperature value [C]")                   # minimal temperature value
        parser.add_argument("--maxTemp",   nargs=1, default=None,       help="maximal temperature value [C]")                   # maximal temperature value
        parser.add_argument("--riseTime",  nargs=1, default=None,       help="change rate from lower to higher temperature")    # temperature change rate in postive temperature direction
        parser.add_argument("--fallTime",  nargs=1, default=None,       help="change rate from lower to higher temperature")    # temperature change rate in negative temperature direction
        # climate chamber
        parser.add_argument("--chamber",    nargs=1, default=[self.avlChambers[0], ],   help="Used climate chamber")                # selected temperature chamber, default ESPEC_SH641
        parser.add_argument("--itfCfgFile", nargs=1, default=None,                      help="Yml interface configuration file")    # interface
        # parse
        args = parser.parse_args(argv[1:])  # first argument is python file name
        # select climate chamber
        chamberArgs = {}
        chamberArgs['chamber'] = args.chamber[0]        # chamber
        chamberArgs['itfCfgFile'] = args.itfCfgFile     # interface config
        # align CLI to wave.py api
        waveArgs = {}                                       # init dict
        waveArgs['ts'] = self.cfg_tsample_sec               # define sample time
        waveArgs['tp'] = self.time_to_sec(args.period[0])   # cast and align
        if ( args.sine and args.trapezoid ):                # dispatch waveform switch
            raise ValueError("Multiple waveform selected")
        elif ( args.sine ):             # sine selected
            waveArgs['wave'] = "sine"
        elif ( args.trapezoid ):        # trapszoid selected
            waveArgs['wave'] = "trapezoid"
        if ( None != args.minTemp ):    # align low temperature
            waveArgs['lowVal'] = float(args.minTemp[0].replace("C", "").replace("c", ""))
        if ( None != args.maxTemp ):    # align high temperature
             waveArgs['highVal'] = float(args.maxTemp[0].replace("C", "").replace("c", ""))
        if (False == (('wave' in waveArgs) and ('lowVal' in waveArgs) and ('highVal' in waveArgs) ) ):  # check for mandatory args
            raise ValueError("Missing mandatory args: wave, lowVal, highVal")
        if ( None != args.riseTime ):   # convert risetime
            waveArgs['tr'] = self.temp_grad_to_time(gradient=args.riseTime[0], deltaTemp=waveArgs['highVal']-waveArgs['lowVal'])
        if ( None != args.fallTime ):
            waveArgs['tf'] = self.temp_grad_to_time(gradient=args.fallTime[0], deltaTemp=waveArgs['highVal']-waveArgs['lowVal'])
        if ( args.invert ):
            waveArgs['pSlope'] = False
        # normal end
        return chamberArgs, waveArgs
    #*****************************

    
    #*****************************
    def time_to_sec(self, time=None):
        """
        @note           detects type of time and converts to seconds in numeric format
                        supported time formats
                          * d:h:m:s
                          * 1d, 1h, 1m, 1s
                            
        @param time     time in seconds or time string
        @rtype          float
        @return         time in seconds as numeric value
        """
        # check empty argument
        if ( None == time ):
            raise ValueError("No time string provided")
        # check if numeric data is provided, treated as seconds    
        elif ( isinstance(time, float) or isinstance(time, int) ):
            return time
        # check for string
        elif ( isinstance(time, str) ):
            # check for pure numeric string
            if ( time.isnumeric() ):
                return float(time)
            # check for ':' separated string
            elif ( -1 != time.find(":") ):
                # collects converted time
                secs = 0
                # prepare for positional to typ conv
                colSep = self.timeColSep.split(":") # make to list
                colSep.reverse()                    # alignment from seconds
                # iterate over segments in reversed order. last element is always sec
                for idx,item in enumerate(reversed(time.split(":"))):
                    # skip empty element
                    if ( 0 == len(item) ): continue
                    # convert to sec
                    try:
                        secs = secs + float(item) * self.timeToSec[colSep[idx]]     # accumulate and convert
                    except:
                        raise Warning("Skipping positional element " + str(idx) + " with value '" + str(item) + "'")
                # release result
                return secs
            # check if string contents elements from 'toSec'
            elif ( time.replace(" ", "").replace(".", "").isalnum() ):
                # prepare time
                secs = 0
                # separate into time substrings
                for timePart in time.split(" "):    # split at blank at iterate
                    # https://stackoverflow.com/questions/12409894/fast-way-to-split-alpha-and-numeric-chars-in-a-python-string/12411196
                    # https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
                    digUnit = re.findall(r"[a-zA-Z_]+|[-+]?\d*\.\d+|\d+", timePart)   # split number from unit
                    if ( 1 == len(digUnit) ):       # handle time w/o numeric multiplier
                        digUnit.append(digUnit[0])  # save base time
                        digUnit[0] = 1              # complete non time base part
                    elif ( 2 < len(digUnit) ):
                        raise Warning("Time string part '" + timePart + "' not convertable, skip...")
                        continue
                    # convert to seconds
                    try:
                        secs = secs + float(digUnit[0]) * self.timeToSec[digUnit[1]]
                    except:
                        raise Warning ("Time unit '" + digUnit[1] + "' unknown")
                # release result
                return secs
            # unrecognized time string
            else:
                raise ValueError("Unrecognized time string '" + time + "'")
        # unkown data type
        else:
            raise TypeError("Unsupported data type '" + str(type(time)) + "'")
    #*****************************
    
    
    #*****************************
    def sec_to_time(self, sec=None, sep=" "):
        """
        @note           Converts given seconds to human readable time format
                        supported time formats
                          * d:h:m:s
                          * 1d, 1h, 1m, 1s
                          
        @param sec      time in seconds, number to convert
        @param sep      separator between time string { col | blank }
        
        @rtype          string
        @return         seconds converted to time string
        """
        # check empty argument
        if ( None == sec ):
            raise ValueError("No time provided")
        if ( 0 > sec ):
            raise ValueError("Only non-negativ secs allowed")
        if ( 0 == sec):
            return (str(0))
        # prepare data set
        secToTime = dict(zip(self.timeToSec.values(), self.timeToSec.keys()))   # swap keys and values
        secIter = sec;                                                          # store in intermediate variable
        timeStr = ""
        # extract base unit and split
        for unitDiv in list(reversed(sorted(secToTime.keys()))):
            # split base unit
            q, r = divmod(secIter, int(unitDiv))
            if (q > 0):
                # base not achieved
                if ( unitDiv > 1 ):
                    timeStr = timeStr + str(int(q))
                # base resolution achieved, take also fracs
                else:
                    timeStr = timeStr + str(secIter)
                # dispatch separator
                if ( sep == " " ):
                    timeStr = timeStr + secToTime[unitDiv][0] + " "
                elif( sep == ":" ):
                    timeStr = timeStr + ":"
                else:
                    raise ValueError("Unsupported separator '" + sep + "'")
                # update remaining time
                secIter = secIter - q*int(unitDiv)
        # drop last char 
        timeStr = timeStr[0:-1]
        # release result
        return timeStr
    #*****************************
    
    
    #*****************************
    def temp_grad_to_time(self, gradient=None, deltaTemp=None):    
        """
        @note               converts given gradient or slew time to seconds
                            supported formats:
                              * 5C/min
                              * 5C/5min
                              * 1min
                            
        @param gradient     time in seconds, number to convert
        @param deltaTemp    min/max temperature difference
        @rtype              float
        @return             slew time from min to max
        """
        # check for gradient
        if ( None == gradient ):
            raise ValueError("No temperature gradient given")
        # check for gradient
        if ( -1 != gradient.find("/") ):
            # check
            if ( None == deltaTemp ):
                raise ValueError("Low/High Temperature value for total slew time required")
            # split time and temp
            temperature = gradient.split("/")[0]
            time = gradient.split("/")[1]
            # prepare
            time = self.time_to_sec(time=time)                              # convert to seconds
            temperature = temperature.replace("C", "").replace("c", "")     # filter celsius
            temperature = temperature.replace("K", "").replace("k", "")     # filter kelvin
            # calc slew time
            slewTime = (abs(deltaTemp) / float(temperature)) * time
        # slew time over complete range
        else:
            slewTime = self.time_to_sec(time=gradient)
        # normal end
        return slewTime
    #*****************************
    
    
    #*****************************
    def open(self, chamberArg=None, waveArg=None):
        """
        @note               prepare chamber and opens for operation
                              * opens interface to chamber
                              * initializes waveform
                            
        @param chamberArg   climate chamber setting
        @param waveArg      waveform settings
        @rtype              boolean
        @return             chamber is operable
        """        
        # check for args
        if ( None == chamberArg or None == waveArg ):
            raise ValueError("Missing args")
        # select chamber
        if ( "sim" == chamberArg['chamber'].lower() ):
            self.chamber = simdev.simChamber()
        elif ( "espec_sh641" == chamberArg['chamber'].lower() ):
            self.chamber = sh_641_drv.especShSu()   # init driver
        else:
            raise ValueError("Unsupported climate chmaber '" + chamberArg['chamber'] +"' selected")
        # open chamber interface
        if ( None != chamberArg['itfCfgFile'] ):
            self.chamber.open(cfgFile = chamberArg['itfCfgFile'])
        else:
            self.chamber.open()
        # init waveform
        self.wave = waves.waves()   # create class
        self.wave.set(**waveArg)    # init waveform
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def start(self):
        """
        @note               prepare chamber and opens for operation
                              * opens interface to chamber
                              * initializes waveform
                            
        @param chamberArg   climate chamber setting
        @param waveArg      waveform settings
        @rtype              boolean
        @return             chamber is operable
        """    
        
        """
        Starts Chamber 
            1) opens interface
            2) initialize chamber
            3) start temperature control
    
        Return:
            True:
            False:
        """
        # check for successfull opening
        if ( (None == self.chamber) or (None == self.wave) ):
            raise ValueError("Interfaces not opened, call method 'open'")
        # set current clima as target clima
        self.chamber.set_clima(self.chamber.get_clima())
        # start chamber
        self.chamber.start()
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def chamber_clima_meas(self):
        """
        measures chambers current values and
        stores result in self.tmeas and self.hmeas
        
        Return:
            True:   all good
            False:  something went wrong
        """
        # dispatch to chamber driver
        if ( self.supported_chamber[self.arg_sel_chamber] == "ESPEC_SH641" ):
            # read value
            temp = self.espesShSu.get_temp()
            # succesful?
            if ( False == temp ):
                print("Error: Read measured temperature from chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
                return False
            # assign to internal
            self.tmeas = temp["measured"]
            # read value
            humi = self.espesShSu.get_humidity()
            # succesful?
            if ( False == humi ):
                print("Error: Read measured humidity from chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
                return False
            # assign
            self.hmeas = humi["measured"]
        else:
            print("Error: Unsupported Chamber")
            return False
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def chamber_clima_set(self):
        """
        Updates chambers climate settings - tempetature and humidity
        
        Return:
            True:   all good
            False:  something went wrong
        """
        # dispatch to chamber driver
        if ( self.supported_chamber[self.arg_sel_chamber] == "ESPEC_SH641" ): 
            # set temperature value
            if ( False == math.isnan(self.tset['val']) ):
                if ( False == self.espesShSu.set_temp(self.tset['val']) ):
                    print("Error set new temperature value to chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
                    return False
            # set humidity
            if ( False == math.isnan(self.hset) ):
                print("Error huminity set from chamber '" + self.supported_chamber[self.arg_sel_chamber] + "' not implemented")
                return False
        else:
            print("Error: Unsupported Chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
            return False
        # graceful end
        return True        
    #*****************************
    
    
    #*****************************
    def wave_update(self, init=False): 
        """
        Based on CLI option calls this function the correponding
        waveform calculation und updates the temperature seting
        point in the class storage objects
        
        """
        # check temperature args
        if ( math.isnan(self.arg_tmin) or math.isnan(self.arg_tmax) ):
            print("Error: Tmin and/or Tmax not initialized")
            return False
        if ( self.arg_tmin > self.arg_tmax ):
            print("Error: Tmin > Tmax")
            return False
        # select calculation function
        # sine, -sine selected
        if ( -1 != self.supported_waveforms[self.arg_sel_waveform].find("sine") ):  
            # check for init
            if ( True == init ):
                # determine sine direction by user
                posSlope = True
                if ( "-" == self.supported_waveforms[self.arg_sel_waveform][0] ):
                    posSlope = False
                # init sine function
                if ( True != self.wave.sine_init(sample=self.cfg_tsample_sec, period=self.arg_periode_sec, low=self.arg_tmin, high=self.arg_tmax, init=self.tmeas, posSlope=posSlope) ):
                    print("Error: Init sine wave")
                    return False
            # normal wave update
            self.tset = self.wave.sine()

                        
        # unsupported Waveform
        else:
            return False
        # check for succesfull wave update
        if ( False == self.tset ):
            print("Error calculate temperature wave update")
            return False
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def cli_update(self):
        """
        Updates command line interface output, clears complete
        comman line window output and rewrites it
        """
        # convert to human readable gradient
        if ( 0 == self.tset['grad'] ):  # handle zero
            grad_str = "0"
        else:                           # try to convert
            # unit of grad is °C/n
            # n   = round(self.arg_periode_sec/self.cfg_tsample_sec)
            # 1/n = self.cfg_tsample_sec / self.arg_periode_sec
            grad = self.tset['grad']                # extract from dict
            grad = grad * 1/self.cfg_tsample_sec    # bring to si unit second
            deg_base_s = min([1, 60, 3600], key=lambda x:abs(x-1/grad)) # get number close to time base, 1/grad = 1°C/n_sec, https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
            grad_base = grad * deg_base_s                               # gradient is realted to 1s, 1min, 1h
            grad_str = "{num:+.{frac}f}".format(num=grad_base, frac=self.num_temps_fracs+1, flags='+') + " °C/" + self.sec_to_timestr(deg_base_s)[1:]
        # Update CLI Interface
        print("\x1b[2J")       # delete complete output
        print("Arbitrary Temperature Waveform Generator")
        print()
        print("  Chamber")
        print("    State    : " + self.spinner.__next__())
        print("    Tmeas    : " + "{num:+.{frac}f} °C".format(num=self.tmeas, frac=self.num_temps_fracs))
        print()
        print("  Waveform")
        print("    Shape    : " + self.supported_waveforms[self.arg_sel_waveform])
        print("    Tmin     : " + "{num:+.{frac}f} °C".format(num=self.arg_tmin, frac=self.num_temps_fracs))
        print("    Tmax     : " + "{num:+.{frac}f} °C".format(num=self.arg_tmax, frac=self.num_temps_fracs))
        print("    Period   : " + self.sec_to_timestr(self.arg_periode_sec))
        print("    Gradient : " + grad_str)
        print("    Tset     : " + "{num:+.{frac}f} °C".format(num=self.tset['val'], frac=self.num_temps_fracs))
        # todo
        
        print()
        print()
        print("Press 'CTRL + C' for exit")
        # graceful end
        return True
    #*****************************
    
    
    #***************************** 
    def main(self):
        """
        Main Routine
        """
        # help constants
        eroEnd = False;
        # parse CLI
        if ( False == self.check_args_set(self.parse_cli(sys.argv)) ):
            print("Error: Parse Args")
            return False
        # start chamber
        #if ( False == self.chamber_start() ):
        #    print("Error: Start chamber")
        #    return False
        # get current temp and init waveform
        

        
        
        self.tmeas=23
        self.wave.trapezoid_init(sample=1, period=3600, low=-10, high=30, rise=10, fall=20, init=self.tmeas, posSlope=True)
        print(str(self.wave.iterator))
        print(self.wave.trapezoid())
        #return True
        
        # initialize waveform
        if ( False == self.wave_update(init=True) ):
            print("Error: init waveform")
            return False
        
        
        # chamber control loop
        while True:
            # runs in a loop
            try:
                # chamber measure current values
                
                # update current temperature set value
                if ( False == self.wave_update() ):
                    print("Error: calculate new temperature set value")
                    eroEnd = True
                    break
                # update user if
                if ( False == self.cli_update() ):
                    print("Error: Update user interface")
                    eroEnd = True
                    break
                # todo
                time.sleep(1)




            # leave chamber control loop
            except KeyboardInterrupt:
                # leave loop on CTRL + C
                print("")
                print("Info: Program normally ended")
                break
            
            
        # init discrete waveform
        #self.arg_periode_sec = 43200
        #self.arg_tmin = -10
        #self.arg_tmax = 60
        #self.calc_wave_sine(init=True)
        #while True:
        #    self.calc_wave_sine()
        #    self.chamber_clima_meas()
        #    self.chamber_clima_set()
        #    time.sleep(self.cfg_tsample_sec)
        #    print("Tset: " + str(self.tset))
        #    print("Tmeas: " + str(self.tmeas))
        pass
    #*****************************
    
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    
    # constuct class
    myATWG = ATWG()
    # call main function
    myATWG.main()

#------------------------------------------------------------------------------
   
