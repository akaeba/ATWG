#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          ATWG.py
@date:          2020-01-04

@note           Arbitrary Temperature Waveform Generator
                  - directly started from command line
                  - run with 'python ./ATWG <myArgs>'
                  - 'run ./ATWG/ATWG.py --sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1h'

@see            https://docs.python.org/3/library/exceptions.html#exception-hierarchy
"""



#------------------------------------------------------------------------------
# Standard
import sys                          # python path handling
import os                           # platform independent paths
import argparse                     # argument parser
import time                         # time
import itertools                    # spinning progress bar
import re                           # regex, needed for number string separation
# Self
from ATWG.waves.waves import waves  # waveform generator
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
        self.clima = {}         # storage element for last measured clima
        # time string conversion
        self.timeToSec = {'s': 1, 'sec': 1, 'm': 60, 'min': 60, 'h': 3600, 'hour': 3600, 'd': 86400, 'day': 86400}   # conversion dictory to seconds
        self.timeColSep = "d:h:m:s"                                                                                  # colon separated time string prototype
        # Progress Spinner
        # SRC: https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
    #*****************************
    
    
    #*****************************
    def parse_cli(self, cliArgs=None):
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
        parser.add_argument("--minTemp",   nargs=1, default=None,       help="waveforms minimal temperature value [C]")         # minimal temperature value
        parser.add_argument("--maxTemp",   nargs=1, default=None,       help="waveforms maximal temperature value [C]")         # maximal temperature value
        parser.add_argument("--startTemp", nargs=1, default=["25C",],   help="start temperature of waveform [C]")               # start temperature value
        parser.add_argument("--riseTime",  nargs=1, default=None,       help="change rate from lower to higher temperature")    # temperature change rate in postive temperature direction
        parser.add_argument("--fallTime",  nargs=1, default=None,       help="change rate from lower to higher temperature")    # temperature change rate in negative temperature direction
        # climate chamber
        parser.add_argument("--chamber",    nargs=1, default=[self.avlChambers[0], ],   help="Used climate chamber")                # selected temperature chamber, default ESPEC_SH641
        parser.add_argument("--itfCfgFile", nargs=1, default=None,                      help="Yml interface configuration file")    # interface
        # parse
        args = parser.parse_args(cliArgs)
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
        if ( False == (('wave' in waveArgs) and ('lowVal' in waveArgs) and ('highVal' in waveArgs) ) ):  # check for mandatory args
            raise ValueError("Missing mandatory args: wave, lowVal, highVal")
        if ( None != args.startTemp ):
            waveArgs['initVal'] = float(args.startTemp[0].replace("C", "").replace("c", ""))
            waveArgs['initVal'] = max(min(waveArgs['initVal'], waveArgs['highVal']), waveArgs['lowVal']) # apply upper and lower fence
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
            timeVal = gradient.split("/")[1]
            # prepare
            timeVal = self.time_to_sec(time=timeVal)                        # convert to seconds
            temperature = temperature.replace("C", "").replace("c", "")     # filter celsius
            temperature = temperature.replace("K", "").replace("k", "")     # filter kelvin
            # calc slew time
            slewTime = (abs(deltaTemp) / float(temperature)) * timeVal
        # slew time over complete range
        else:
            slewTime = self.time_to_sec(time=gradient)
        # normal end
        return slewTime
    #*****************************
    
    
    #*****************************
    def normalize_gradient(self, grad_sec=None):
        """
        @note               normalizes dividend with increasing divisor with 
                            the goal to achieve a one in the dividend
                            
        @param grad_sec     time in seconds, number to convert
        @rtype              string
        @return             human readable gradient
        """
        # check for gradient
        if ( None == grad_sec ):
            raise ValueError("No temperature gradient given")
        # stuck rates smaller then 8 fracs to zero
        if ( 0 == float("{num:+.{frac}f}".format(num=grad_sec, frac=8))):
            return {'val': grad_sec, 'base': 's'}
        # determine timebase to once digit
        for tb in self.timeToSec.values():
            digit = float(grad_sec) * float(tb)
            base = tb
            if ( abs(digit) >= 1.0 ):
                break
        # build result dict
        try:        # conv to human readable time
            return {'val': digit, 'base': self.sec_to_time(sec=base)[1:]}
        except:     # no conv in case of ero
            return {'val': grad_sec, 'base': 's'}
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
        @return             successful
        """        
        # check for args
        if ( None == chamberArg or None == waveArg ):
            raise ValueError("Missing args")
        # select chamber
        if ( "sim" == chamberArg['chamber'].lower() ):
            from ATWG.driver.sim.simChamber import simChamber   # import if required
            self.chamber = simChamber()
        elif ( "espec_sh641" == chamberArg['chamber'].lower() ):
            from ATWG.driver.espec.sh641 import especShSu       # import if required
            self.chamber = especShSu()                          # init driver
        else:
            raise ValueError("Unsupported climate chmaber '" + chamberArg['chamber'] +"' selected")
        # open chamber interface
        if ( None != chamberArg['itfCfgFile'] ):
            self.chamber.open(cfgFile = chamberArg['itfCfgFile'])
        else:
            self.chamber.open()
        # init waveform
        self.wave = waves()         # create class
        self.wave.set(**waveArg)    # init waveform
        # normal end
        return True
    #*****************************
    
    
    #*****************************
    def start(self):
        """
        @note               starts chamber with operation
                              * set temperature is current temperature
                            
        @rtype              boolean
        @return             successful
        """
        # check for successfull opening
        if ( (None == self.chamber) or (None == self.wave) ):
            raise ValueError("Interfaces not opened, call methode 'open'")
        # set current clima as target clima
        self.chamber.set_clima(clima=self.chamber.get_clima())
        # start chamber
        self.chamber.start()
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def stop(self):
        """
        @note               stops chamber operation and set temperature to waveform start value
                            
        @rtype              boolean
        @return             successful
        """
        # set chamber to start value
        self.chamber.set_clima(clima={'temperature': self.wave.waveArgs['initVal']})
        # stop chamber
        self.chamber.stop()
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def chamber_update(self):
        """
        @note               updates chamber settings
                              * reads from chamber current clima conditions
                              * set new temperture values
                            
        @rtype              boolean
        @return             successful
        """
        # check for successfull opening
        if ( (None == self.chamber) or (None == self.wave) ):
            raise ValueError("Interfaces not opened, call methode 'open'")
        # acquire current clima
        self.clima['get'] = self.chamber.get_clima();
        # calc next clima value
        self.clima['set'] = self.wave.next();
        # set chamber value
        self.chamber.set_clima(clima={'temperature': self.clima['set']['val']})
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def cli_update(self):
        """
        @note       Updates command line interface output, clears complete
                    comman line window output and rewrites it
                            
        @rtype      boolean
        @return     successful
        """
        # acquire vals
        numFracs = self.chamber.info()['fracs']['temperature']
        grad_norm = self.normalize_gradient(grad_sec=self.clima['set']['grad'])
        # Update CLI Interface
        print("\x1b[2J")       # delete complete output
        print("Arbitrary Temperature Waveform Generator")
        print()
        print("  Chamber")
        print("    State    : Run " + self.spinner.__next__())
        print("    Type     : " + self.chamber.info()['name'])
        print("    Tmeas    : " + "{num:+.{frac}f} °C".format(num=self.clima['get']['temperature'], frac=numFracs))
        print("    Tset     : " + "{num:+.{frac}f} °C".format(num=self.clima['set']['val'], frac=numFracs))
        print()
        print("  Waveform")
        print("    Shape    : " + self.wave.waveArgs['wave'])
        print("    Tmin     : " + "{num:+.{frac}f} °C".format(num=self.wave.waveArgs['lowVal'], frac=numFracs))
        print("    Tmax     : " + "{num:+.{frac}f} °C".format(num=self.wave.waveArgs['highVal'], frac=numFracs))
        print("    Period   : " + self.sec_to_time(sec=self.wave.waveArgs['tp']))
        print("    Gradient : " + "{num:+.{frac}f} °C".format(num=grad_norm['val'], frac=numFracs) + "/" + grad_norm['base'])
        print()
        print()
        print("Press 'CTRL + C' for exit")
        # graceful end 
        return True
    #*****************************
    
    
    #*****************************
    def close(self):
        """
        @note               cloeses hw handle to chamber
                            
        @rtype              boolean
        @return             successful
        """
        # close chamber handle
        self.chamber.close()
        # graceful end
        return True
    #*****************************
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    
    myATWG = ATWG()                                                                                         # constuct class
    chamberArg, waveArg = myATWG.parse_cli(["--sine", "--minTemp=20C", "--maxTemp=30C", "--chamber=SIM"])   # set option
    myATWG.open(chamberArg=chamberArg, waveArg=waveArg)                                                     # init waveformgenertor and open chamber interface
    myATWG.chamber_update()                                                                                 # update chamber
    myATWG.cli_update()                                                                                     # update UI
    myATWG.stop()
    myATWG.close()
#------------------------------------------------------------------------------
