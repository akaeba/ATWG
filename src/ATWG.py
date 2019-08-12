# -*- coding: utf-8 -*-
"""
Arbitrary temperature waveform generator
"""

__FILE__         = "ATWG.py"
__author__ 		= "Andreas Kaeberlein"
__copyright__ 	= "Copyright 2019, Arbitrary Temperature Waveform Generator"
__credits__      = ["AKAE"]

__license__      = "LGPLv3"
__version__      = "0.1.0"
__maintainer__ 	= "Andreas Kaeberlein"
__email__        = "andreas.kaeberlein@web.de"
__status__       = "Development"



#------------------------------------------------------------------------------
import sys                      # CLI arguments
import argparse                 # argument parser
import time                     # time
import math                     # sine
import espec_corp_sh_641_drv    # driver for climate chamber
import itertools                # spinning progress bar
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
        # features
        self.supported_chamber = ["ESPEC_SH641",]      # supported temperature chambers
        self.supported_waveforms = ["const", "sine"]   # implemented waveform algorithms
        # collected args
        self.arg_sel_chamber = float("nan")   # selected chambers
        self.arg_sel_waveform = float("nan")  # choosen waveform
        self.arg_itf = ""                     # communication interface
        self.arg_periode_sec = float("nan")   # waveform periode in seconds
        self.arg_tmin = float("nan")          # minimal temperature in function
        self.arg_tmax = float("nan")          # maximal temerpature in function
        # discrete waveform calculation
        self.wave_iterator = 0          # waveform iterator
        # temperture setting
        self.tset = float("nan")        # setted temperature
        self.tmeas = float("nan")       # measured temperature
        self.hset = float("nan")        # setted humidity
        self.hmeas = float("nan")       # measured humidity
        # supported chamber classes
        self.espesShSu = espec_corp_sh_641_drv.especShSu()    # create class without constructor call
        # chamber measurement resolution
        self.num_temps_fracs = 1   # temperature measurement fracs
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
        parser.add_argument("--tmin",      nargs=1, default=[float("nan"),],                help="minimal temperature value [°C]")        # minimal temperature value
        parser.add_argument("--tmax",      nargs=1, default=[float("nan"),],                help="maximal temperature value [°C]")        # minimal temperature value
        parser.add_argument("--tset",      nargs=1, default=float(25),                      help="set temperature value     [°C]")        # minimal temperature value
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
            self.arg_periode_sec = self.conv_time(args.period[0])
        except:
            print("Error: Can't handle time format '" + args.period[0] + "'")
            return False
        
        # copy to internal
        self.arg_itf = args.interface[0]
        self.arg_tmin = args.tmin[0]
        self.arg_tmax = args.tmax[0]
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def conv_time(self, timeStr = ""):
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
        # check for colon based formats
        if ( -1 != timeStr.find(":") ):
            # iterate over segments in reversed order. last element is always sec
            for idx,item in enumerate(reversed(timeStr.split(":"))):
                # skip empty element
                if ( 0 == len(item) ):
                    print("Bla")
                    continue
                # check for max elem
                if ( 2 < idx ):
                    print("Warning: only last three elements in '" + timeStr + "' processed")
                    break
                # process to time
                secs = secs + float(item) * pow(60, idx)
            # leave
            return secs
        # check SI units
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
            if ( False == math.isnan(self.tset) ):
                if ( False == self.espesShSu.set_temp(self.tset) ):
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
    def calc_wave_sine(self, init=False, tstart=None):
        """
        Calculates Sine Waveform
        
        Return:
            New Tempvalue
        """
        # check set
        if ( math.isnan(self.arg_tmin) or math.isnan(self.arg_tmax) ):
            print("Error: Tmin and/or Tmax not initialized")
            return False
        # check order
        if ( self.arg_tmin > self.arg_tmax ):
            print("Error: Tmin > Tmax")
            return False
        # calc amplitude
        tamp = (self.arg_tmax - self.arg_tmin) / 2
        tofs = tamp + self.arg_tmin
        # initialized
        if ( True == init ):
            self.wave_iterator = 0      # todo calc close to tset
        # calculate discrete sine
        self.tset = tofs + tamp*(math.sin(2 * math.pi * ( self.wave_iterator * self.cfg_tsample_sec / self.arg_periode_sec)))
        self.wave_iterator += 1
        # jump to sine start
        if ( self.wave_iterator > self.arg_periode_sec - 1):
            self.wave_iterator = 0
        # graceful end
        return True
    #*****************************
    
    
    #***************************** 
    def main(self):
        """
        Main Routine
        """
        # Progress Spinner
        # SRC: https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        # parse CLI
        if ( False == self.check_args_set(self.parse_cli(sys.argv)) ):
            print("Error: Parse Args")
            return False
        # start chamber
        #if ( False == self.chamber_start() ):
        #    print("Error: Start chamber")
        #    return False
        # get current temp and init waveform
        
        
        # infinite loop, ends at keyboard interrupt
        print(str(self.conv_time("5min")))
        
        
        # chamber control loop
        while True:
            # runs in a loop
            try:
                # do chamber stuff
                
                
                # Update CLI Interface
                print("\x1b[2J")       # delete complete output
                print("Arbitrary Temperature Waveform Generator")
                print()
                print("  State    : " + spinner.__next__())
                print("  Waveform : " + self.supported_waveforms[self.arg_sel_waveform])
                print("  Gradient : ")
                print("  Tset     : " + "{num:.{frac}f} °C".format(num=self.tset, frac=self.num_temps_fracs))
                print("  Tmeas    : " + "{num:.{frac}f} °C".format(num=self.tmeas, frac=self.num_temps_fracs))
                
                print()
                print()
                print("Press 'CTRL + C' for exit")
                # 
                
                
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
   
