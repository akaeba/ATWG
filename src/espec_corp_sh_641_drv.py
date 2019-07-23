#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides basic functions to interface the climate chamber
 * ESPEC CORP. SH-641
"""

__author__ 		= "Andreas Kaeberlein"
__copyright__ 	= "Copyright 2018, Arbitrary Temperature Waveform Generator"
__credits__     = ["AKAE"]

__license__ 	= "LGPLv3"
__version__ 	= "0.1.0"
__maintainer__ 	= "Andreas Kaeberlein"
__email__ 		= "andreas.kaeberlein@web.de"
__status__ 		= "Development"


#------------------------------------------------------------------------------
import importlib.util   # submodule dependcy check
import serial           # COM port Interface
import espec_sh_ist
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class especShSu:
    #*****************************
    # Constants
    GET_TYPE="TYPE?"
    #*****************************
    
    
    #*****************************
    def __init__(self):
        """
        Initialisation of class
        """
        # Com port Settings
        self.com_port=7             # default is Com Port 1
        self.com_baudrate=9600      # set baudrate
        self.com_databit=8
        self.com_stopbit=1
        self.com_parity="none"
        
        # serial in/out variables
        self.ser_out = ""
        self.ser_in = ""
       
    #*****************************
 
    
    #*****************************   
    def check_dependency(self):
        """
        Checks if required packages are installed
        SRC: https://stackoverflow.com/questions/1051254/check-if-python-package-is-installed
        
        Return:
            True:   no dependcy missing
            False:  dependency missing 
        """
        check_pkg = ("serial",)
        for pkg in check_pkg:
            isPresent = importlib.util.find_spec(pkg)
            if isPresent is None:
                print(pkg +" is not installed")
                return False
        return True
    #*****************************
        

    #*****************************   
    def open(self):
        """
        Opens COM port and try to recognize the climate chamber
        SRC: http://www.varesano.net/blog/fabio/serial%20rs232%20connections%20python
        """
        # allign to py serial
        port = "COM" + str(self.com_port)
        if ( self.com_stopbit == 1 ):
            stopbit = serial.STOPBITS_ONE
        elif ( self.com_stopbit == 2 ):
            stopbit = serial.STOPBITS_TWO
        else:
            print("Error: stopbits=", str(self.com_stopbit), " unsupported")
            return False
        if ( self.com_parity == "none"):
            parity = serial.PARITY_NONE
        else:
            print("Error: parity=", self.com_parity, " unsupported")
        if ( self.com_databit == 8 ):
            databit = serial.EIGHTBITS
        else:
            print("Error: databit=", self.com_databit, " unsupported")
        
        # configure IF
        self.com = serial.Serial(
                     port=port,
                     baudrate=self.com_baudrate,
                     stopbits=stopbit,
                     parity=parity,
                     bytesize=databit
                   )
        
        # open COM interface
        if ( False == self.com.isOpen() ):
            print("Failed open COM interface ", str(self.com_port))
            return False

        # check Type
        self.ser_out = espec_sh_ist.GET_TYPE + espec_sh_ist.LINE_END    # request chamber type
        self.serial_write()
        self.serial_read()
        
        
        
        
    #*****************************
    
    
    #*****************************   
    def close(self):
        """
        Closes Handle
        """
        self.com.close()
    #***************************** 
    
    
    #*****************************   
    def serial_write(self):
        """
        Writes buffer to serial port
        """
        # check interface is open
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return False
        # write to com
        self.com.write(self.ser_out.encode())
        # clear
        self.ser_out = ""
        # normal end
        return True
    #*****************************
    
    
    #*****************************   
    def serial_read(self):
        """
        Reads from serial port into buffer
        
        return: ser_in
        """     
        # check interface is open 
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return False
        # make empty
        self.ser_in = ""
        # read from COM
        while ( False == (espec_sh_ist.LINE_END in self.ser_in) ):
            byte = self.com.read(1);
            self.ser_in += byte.decode()
        # drop line end
        self.ser_in = self.ser_in[:-len(espec_sh_ist.LINE_END)]
        # normal end
        return True
     #*****************************
     

    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    
    myChamber = especShSu()        # call class constructor
    myChamber.open()
    myChamber.close()
    
#------------------------------------------------------------------------------
    