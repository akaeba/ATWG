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
        # discrete waveform calculation
        self.wave_iterator = 0          # waveform iterator
        # temperture setting
        self.tset = float("nan")        # setted temperature
        self.tmeas = float("nan")       # measured temperature
        self.hset = float("nan")        # setted humidity
        self.hmeas = float("nan")       # measured humidity
        # supported chamber classes
        self.espesShSu = espec_corp_sh_641_drv.especShSu()    # create class without constructor call
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
        parser.add_argument("--twave",     nargs=1, default=[self.supported_waveforms[0],], help="temperature waveform")              # temperature shape
        parser.add_argument("--tmin",      nargs=1, default=float("nan"),                   help="minimal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tmax",      nargs=1, default=float("nan"),                   help="maximal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tset",      nargs=1, default=float(25),                      help="set temperature value     [°C]")    # minimal temperature value
        parser.add_argument("--chamber",   nargs=1, default=[self.supported_chamber[0],],   help="Type of temperature chamber")       # selected temperature chamber, default ESPEC_SH641
        parser.add_argument("--interface", nargs=1, default=["COM1",],                      help="Interface of temperature chamber")  # interface
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
            self.arg_sel_waveform = self.supported_waveforms.index(args.twave[0])
        except:
            print("Error: Temperature waveform '" + args.twave[0] + "' unsupported")
            return False
        # copy to internal
        self.arg_itf = args.interface[0]
        
        return True
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
            if ( float("nan") != self.tset ):
                if ( False == self.espesShSu.set_temp(self.tset) ):
                    print("Error set new temperature value to chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
                    return False
            # set humidity
            #if ( float("nan") != self.hset ):
            #    print("Error huminity set from chamber '" + self.supported_chamber[self.arg_sel_chamber] + "' not implemented")
            #    return False
        else:
            print("Error: Unsupported Chamber '" + self.supported_chamber[self.arg_sel_chamber] + "'")
            return False
        # graceful end
        return True        
    #*****************************
    
    
    #*****************************
    def calc_wave_sine(self, init=False):
        """
        Calculates Sine Waveform
        
        Return:
            New Tempvalue
        """
        # check set
        if ( self.arg_tmin == float("nan") or self.arg_tmax == float("nan") ):
            print("Error: Tmin or Tmax not initialized")
            return False
        # check order
        if ( self.arg_tmin > self.arg_tmax ):
            print("Error: Tmin > Tmax")
            return False
        # calc amplitude
        tamp = (self.arg_tmax - self.arg_tmin) / 2
        tofs = tamp + self.arg_tmin
        # initilaized
        if ( True == init ):
            self.wave_iterator = 0      # todo calc close to tset
        # calculate discrte sine
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
        # parse CLI
        if ( False == self.check_args_set(self.parse_cli(sys.argv)) ):
            print("Error: Parse Args")
            sys.exit(False)
        # start chamber
        if ( False == self.chamber_start() ):
            print("Error: Start chamber")
            sys.exit(False)
        # init discrete waveform
        self.arg_periode_sec = 43200
        self.arg_tmin = -10
        self.arg_tmax = 60
        self.calc_wave_sine(init=True)
        while True:
            self.calc_wave_sine()
            self.chamber_clima_meas()
            self.chamber_clima_set()
            time.sleep(self.cfg_tsample_sec)
            print("Tset: " + str(self.tset))
            print("Tmeas: " + str(self.tmeas))
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
   
