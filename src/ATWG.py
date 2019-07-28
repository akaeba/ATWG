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
#import espec_corp_sh_641_drv    # driver for climate chamber
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class ATWG:
    #*****************************
    def __init__(self):
        """
        Initialization
        """
        self.supported_chamber = ["ESPEC_SH641",]      # supported temperature chambers
        self.selected_chamber = float("nan")           # selected chambers
        self.supported_waveforms = ["const", "sine"]   # implemented waveform algorithms
        self.selected_waveform = float("nan")          # choosen waveform

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
        parser.add_argument("--temp",      nargs=1, default=[self.supported_waveforms[0],], help="temperature waveform")              # temperature shape
        parser.add_argument("--tmin",      nargs=1, default=float("nan"),                   help="minimal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tmax",      nargs=1, default=float("nan"),                   help="maximal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tset",      nargs=1, default=float(25),                      help="set temperature value     [°C]")    # minimal temperature value
        parser.add_argument("--chamber",   nargs=1, default=[self.supported_chamber[0],],   help="Type of temperature chamber")       # selected temperature chamber, default ESPEC_SH641
        parser.add_argument("--interface", nargs=1, default="COM1",                         help="Interface of temperature chamber")  # interface
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
            self.selected_chamber = self.supported_chamber.index(args.chamber[0]);
        except:
            print("Error: Chamber '" + args.chamber[0] + "' not supported")
            print("         use", self.supported_chamber)
            return False
        # check waveform
        try:
            self.selected_waveform = self.supported_waveforms.index(args.temp[0])
        except:
            print("Error: Temperature waveform '" + args.temp[0] + "' unsupported")
            return False
        # fill in limits
        
        
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
            return False
        # call function for
        
        
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
   
