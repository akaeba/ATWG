# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
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
"""



#------------------------------------------------------------------------------
import sys                      # CLI arguments
import argparse                 # argument parser
import time                     # time
import datetime                 # convert second to human redable time
import math                     # sine
import espec_corp_sh_641_drv    # driver for climate chamber
import itertools                # spinning progress bar
import waves                    # waveform calculation
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class ATWG:
    #*****************************
    def __init__(self):
        """
        Initialization
        """
        # config
        self.cfg_tsample_sec = 1   # sample time is 1sec
        # supported temperature chambers
        self.supported_chamber = ["ESPEC_SH641",]
        # waveform calculator
        self.wave = waves.waves()               # create waves object
        # implemented waveforms
        self.supported_waveforms = ["const", "sine", "-sine", "trapezoid"]
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
        self.espesShSu = espec_corp_sh_641_drv.especShSu()    # create class without constructor call
        # chamber measurement resolution
        self.num_temps_fracs = 1   # temperature measurement fracs
        # Progress Spinner
        # SRC: https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
    #*****************************
    
    
    #*****************************
    def parse_cli(self, argv):
        """
        Parses Arguments from Command line
        SRC: https://docs.python.org/3.3/library/argparse.html
        
        Return:
            parsed arguments in structure
        """
        # create object
        parser = argparse.ArgumentParser(description="Generats arbitrary temperature waveform pattern") # create class
        # add args
        parser.add_argument("--wave",      nargs=1, default=[self.supported_waveforms[0],], help="temperature waveform")                  # temperature shape
        parser.add_argument("--tmin",      nargs=1, default=["nan",],                       help="minimal temperature value [°C]")        # minimal temperature value
        parser.add_argument("--tmax",      nargs=1, default=["nan",],                       help="maximal temperature value [°C]")        # minimal temperature value
        parser.add_argument("--chamber",   nargs=1, default=[self.supported_chamber[0],],   help="Type of temperature chamber")           # selected temperature chamber, default ESPEC_SH641
        parser.add_argument("--interface", nargs=1, default=["COM1",],                      help="Interface of temperature chamber")      # interface
        parser.add_argument("--period",    nargs=1, default=["1h",],                        help="Period duration of selected waveform")  # interface
        # parse
        args = parser.parse_args(argv[1:])
        # normal end
        return args
    #*****************************

    
    #*****************************
    def check_args_set(self, args):
        """
        Plausibility check of provided arguments and set of common
        data structure
        
        Return:
            True:   succesful checked and set
            False:  something went wrong
        """
        # check selected chamber
        try:
            self.arg_sel_chamber = self.supported_chamber.index(args.chamber[0]);
        except:
            print("Error: Chamber '" + args.chamber[0] + "' not supported")
            print("         use", self.supported_chamber)
            return False
        # check waveform
        try:
            self.arg_sel_waveform = self.supported_waveforms.index(args.wave[0])
        except:
            print("Error: Temperature waveform '" + args.wave[0] + "' unsupported")
            return False
        # handle period
        try:
            self.arg_periode_sec = self.timestr_to_sec(args.period[0])
        except:
            print("Error: Can't handle time format '" + args.period[0] + "'")
            return False
        
        # copy to internal
        self.arg_itf = args.interface[0]
        self.arg_tmin = float(args.tmin[0])
        self.arg_tmax = float(args.tmax[0])
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def timestr_to_sec(self, timeStr = ""):
        """
        Converts string into integer in secounds
        
        https://www.ibm.com/support/knowledgecenter/en/SSLVMB_23.0.0/spss/base/syn_date_and_time_date_time_formats.html
        
        Return:
            Integer:  number of seconds
            False:    something went wrong
        """
        # check for empty string
        if ( 0 == len(timeStr) ):
            print("Error: Zero length time string provided")
            return False
        # time value
        secs = 0
        # check for colon based formats, hh:mm:ss
        if ( -1 != timeStr.find(":") ):
            # iterate over segments in reversed order. last element is always sec
            for idx,item in enumerate(reversed(timeStr.split(":"))):
                # skip empty element
                if ( 0 == len(item) ):
                    continue
                # check for max elem
                if ( 2 < idx ):
                    print("Warning: only last three elements in '" + timeStr + "' processed")
                    break
                # process to time
                secs = secs + float(item) * pow(60, idx)
            # leave
            return secs
        # check SI units, 1h, 1min, 1sec
        if ( -1 != timeStr.find("s") ):
           secs = round(float(timeStr.replace("sec", "").replace("s", "")))
           return secs
        elif ( -1 != timeStr.find("m") ):
            secs = 60 * float(timeStr.replace("min", "").replace("m", ""))
            return secs
        elif ( -1 != timeStr.find("h") ):
            secs = 3600 * float(timeStr.replace("h", ""))
            return secs
        # end w/o match
        print("Error: Unsupported Time format '" + timeStr + "' provided")
        return False
    #*****************************
    
    
    #*****************************
    def sec_to_timestr(self, sec=0):
        """
        Converts given number and unit to human readable string
        """
        # check for arguemnt
        if ( 0 == sec ):
            return str(sec)
        elif ( 60 > sec ):
            return "{num:.{frac}f}sec".format(num=sec, frac=0)
        elif ( (3600 > sec) and (0 == (sec % 60)) ):
            return "{num:.{frac}f}min".format(num=sec/60, frac=0)
        elif ( 0 == (sec % 3600) ):
            return "{num:.{frac}f}h".format(num=sec/3600, frac=0)
        # default
        return str(datetime.timedelta(seconds=sec))   # h:mm:ss
    #*****************************
    
    
    #*****************************
    def chamber_start(self):
        """
        Starts Chamber 
            1) opens interface
            2) initialize chamber
            3) start temperature control
    
        Return:
            True:
            False:
        """
        # open phy interface to chamber
        if ( self.supported_chamber[self.arg_sel_chamber] == "ESPEC_SH641"):
            # call constructor with port
            if ( False == self.espesShSu.config_com(port=self.arg_itf) ):
                return False
            # open interface to chamber
            if ( False == self.espesShSu.open() ):
                return False
            # set temp to 25°C
            if ( False == self.espesShSu.set_temp(25) ):
                return False
            # start chamber
            if ( False == self.espesShSu.start() ):
                return False
            # get resoluion from chamber
            self.num_temps_fracs = self.espesShSu.get_resolution_fracs()["temperature"]

        else:
            print("Error: Unsupported Chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
            return False
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
   
