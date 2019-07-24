#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides basic functions to interface the climate chamber
 * ESPEC CORP. SH-641
"""

__FILE__       = ""
__author__     = "Andreas Kaeberlein"
__copyright__  = "Copyright 2018, Arbitrary Temperature Waveform Generator"
__credits__    = ["AKAE"]

__license__    = "LGPLv3"
__version__    = "0.1.0"
__maintainer__ = "Andreas Kaeberlein"
__email__      = "andreas.kaeberlein@web.de"
__status__     = "Development"


#------------------------------------------------------------------------------
import importlib.util   # submodule dependcy check
import serial           # COM port Interface
import espec_sh_def
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class especShSu:

    #*****************************
    def __init__(self):
        """
        Initialisation of class
        """
        # Com port Settings
        self.com_port = "COM7"        # default is Com Port 1
        self.com_baudrate = 9600      # set baudrate
        self.com_databit = 8          # data bits
        self.com_stopbit = 1
        self.com_parity = "none"
        self.chamber_isOpen = False
        
        # internal
        self.last_write_temp = float('nan') # stores last written value, used for reduction
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
                return -1
        return 0
    #*****************************
        

    #*****************************
    def open(self):
        """
        Opens COM port and try to recognize the climate chamber
        SRC: http://www.varesano.net/blog/fabio/serial%20rs232%20connections%20python
        """
        # allign to py serial
        if ( self.com_stopbit == 1 ):
            stopbit = serial.STOPBITS_ONE
        elif ( self.com_stopbit == 2 ):
            stopbit = serial.STOPBITS_TWO
        else:
            print("Error: stopbits=", str(self.com_stopbit), " unsupported")
            return -1
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
                     port=self.com_port,
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
        self.chamber_write(espec_sh_def.CMD_GET_TYPE)
        chamberID = self.chamber_read()
        if ( False == chamberID ):
           print("Error: CMD_GET_TYPE")
           return False
        elif ( False == (espec_sh_def.RSP_CH_ID in chamberID) ):
           print("Chamber '" + chamberID + "' unknown")
           return False
        self.chamber_isOpen = True
    #*****************************
    
    
    #*****************************
    def close(self):
        """
        Closes Handle
        """
        self.com.close()
        self.chamber_isOpen = False
    #***************************** 
    
    
    #*****************************
    def chamber_write(self, msg):
        """
        Writes buffer to serial port
        """
        # append termination
        msg += espec_sh_def.MSC_LINE_END
        # check interface is open
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return -1
        # write to com
        self.com.write(msg.encode())
        # normal end
        return 0
    #*****************************
    
    
    #*****************************
    def chamber_read(self):
        """
        Reads from serial port into buffer
        
        Return:
            False:   Somehting went wrong
            String:  Response
        """     
        # check interface is open 
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return False
        # make empty
        msg = ""
        # read from COM
        while ( False == (espec_sh_def.MSC_LINE_END in msg) ):
            byte = self.com.read(1);
            msg += byte.decode()
        # drop line end and return
        msg = msg[:-len(espec_sh_def.MSC_LINE_END)]     # skip CRNL
        msg = msg.strip()                               # skip trailing/leading blanks
        # check for error
        if ( False == self.chk_ero(msg) ):
            print("Error: Chamber Reponse '"+ msg + "'")
            return False
        return msg
     #*****************************
     
     
    #*****************************
    def chk_ero(self, msg):
        """
        Checks reponse message for Error and forwards only if no error
        
        Return:
            False: Somehting went wrong
            True:  All okay
        """
        if ( True == (espec_sh_def.MSC_ERO_CMD in msg) ):
            return False;
        elif ( True == (espec_sh_def.MSC_ERO_PRM in msg) ):
            return False;
        return True
    #*****************************

    
    #*****************************
    def get_temp(self):
        """
        Get Actual Temperature and configuration
        
        Return
            False: Somehting went wrong
            Dictionary:
                measured
                setpoint
                upalarm
                lowalarm
        """
        # check if interface is open 
        if ( False == self.chamber_isOpen ):
            return False
        # Request Limits
        self.chamber_write(espec_sh_def.CMD_GET_TEMP)
        # Read Response, f.e. 26.4,0.0,140.0,-50.0
        rsp = self.chamber_read()
        # assign no dict
        i = 0
        temperature = {}
        for elem in rsp.split(','):
            if ( 0 == i ):
                temperature['measured'] = float(elem.strip())  # measured-temperature
            if ( 1 == i ):
                temperature['setpoint'] = float(elem.strip())  # temperature-set-point
            if ( 2 == i ):
                temperature['upalarm'] = float(elem.strip())   # temperature-upper-limit-alarm-value
            if ( 3 == i ):
                temperature['lowalarm'] = float(elem.strip())  # temperature-lower-limit-alarm-value
            i+=1
        # check for all elements
        if ( 4 != i ):
            print("Uncomplete Temperature Reponse '" + rsp + "'")
            return False
        # return dict
        return temperature
    #*****************************     
            

    #*****************************
    def set_temp(self, temperature):
        """
        Set Chambers new temperature value
        
        Return
            False: Somehting went wrong
        """
        # check if interface is open 
        if ( False == self.chamber_isOpen ):
            return False
        # check if update is necessary
        if ( float('nan') != self.last_write_temp ):
            if ( espec_sh_def.MSC_TEMP_RESOLUTION >= abs(self.last_write_temp-temperature) ):
                return True
        # store last written temperature
        self.last_write_temp = temperature
        # prepare number string
        numDigits = len(str(espec_sh_def.MSC_TEMP_RESOLUTION).split(".")[1])
        setTemp = '{temp:.{frac}f}'.format(temp=temperature, frac=numDigits)
        # send set temperature command
        self.chamber_write(espec_sh_def.CMD_SET_TEMP+setTemp)
        # get response from chamber        
        rsp = self.chamber_read();
        # check for ack, f.e. OK:TEMP,S35
        if ( False == (espec_sh_def.RSP_TEMP_OK in rsp) ):
            print("Error: Set Temperature failed, RSP='" + rsp + "'")
            return False
        # extract temperature, OK:TEMP,S35 -> S35 -> 35.x
        getTemp = rsp.split(",")[1]     # split at ','
        getTemp = getTemp[1:]           # drop 'S'
        getTemp = '{temp:.{frac}f}'.format(temp=float(getTemp), frac=numDigits)
        # check for set
        if ( getTemp != setTemp ):
            print("Error: Chamber not acknowledge new temperature set="+setTemp+" ack="+getTemp)
            return False
        # graceful end
        return True
    #*****************************
       
        
        
    
        

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    
    myChamber = especShSu()        # call class constructor
    myChamber.open()
    print(myChamber.get_temp())
    myChamber.set_temp(25)
    myChamber.close()

    
#------------------------------------------------------------------------------
    