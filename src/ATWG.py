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
import sys                      # 
import argparse                 # argument parser
#import espec_corp_sh_641_drv    # driver for climate chamber
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class ATWG:
    #*****************************
    def __init__(self):
        """
        Initialization
        """
        self.supported_chamber = ["ESPEC_SH641"]    # supported temperature chambers
        self.selected_chamber = ""                  # selected chambers

    #*****************************
    
    
    #*****************************
    def parse_cli(self, argv):
        """
        Parses Arguments from Command line
        
        SRC: https://docs.python.org/3.3/library/argparse.html
        """
        # create object
        parser = argparse.ArgumentParser(description="Generats arbitrary temperature waveform pattern") # create class
        # add args
        parser.add_argument("--temp",    nargs=1, default="const",                   help="temperature waveform")              # temperature shape
        parser.add_argument("--tmin",    nargs=1, default=float("nan"),              help="minimal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tmax",    nargs=1, default=float("nan"),              help="maximal temperature value [°C]")    # minimal temperature value
        parser.add_argument("--tset",    nargs=1, default=float(25),                 help="set temperature value     [°C]")    # minimal temperature value
        parser.add_argument("--chamber", nargs=1, default=self.supported_chamber[0], help="Temperature chamber type")          # selected temperature chamber, default ESPEC_SH641
        
        
        # parse
        args = parser.parse_args(argv[1:])
        # fill in
        
        print(args)
        
        
        
        return True
    #*****************************
        
    
    #***************************** 
    def main(self):
        """
        Main Routine
        """
        # parse CLI
        self.parse_cli(sys.argv)
        
        
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
   
