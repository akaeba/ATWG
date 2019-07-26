#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides basic functions to interface the climate chamber
 * ESPEC CORP. SH-641
"""

__FILE__       = "espec_corp_sh_641_drv.py"
__author__     = "Andreas Kaeberlein"
__copyright__  = "Copyright 2018, Arbitrary Temperature Waveform Generator"
__credits__    = ["AKAE"]

__license__    = "LGPLv3"
__version__    = "0.1.0"
__maintainer__ = "Andreas Kaeberlein"
__email__      = "andreas.kaeberlein@web.de"
__status__     = "Development"


#------------------------------------------------------------------------------
import importlib.util   # submodule dependency check
import serial           # COM port Interface
import espec_sh_def     # climate chamber defintions
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class especShSu:

    #*****************************
    def __init__(self, comPort="COM1"):
        """
        Initialisation of class
        """
        # Com port Settings
        self.com_port = comPort       # default is Com Port 1
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
        # align to py serial
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
        if ( False == self.chamber_write(espec_sh_def.CMD_GET_TYPE) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_GET_TYPE + "'")
            return False
        chamberID = self.chamber_read()
        if ( False == chamberID ):
           print("Error: CMD_GET_TYPE")
           return False
        elif ( False == (espec_sh_def.RSP_CH_ID in chamberID) ):
           print("Error: Chamber '" + chamberID + "' unknown")
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
            return False
        # write to com
        self.com.write(msg.encode())
        # normal end
        return True
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
        msg = msg.replace(' ', '')                      # remove all blanks
        return msg
    #*****************************


    #*****************************
    def parse_set_rsp(self, msg):
        """
        Parses response of set command

        Argument:
            msg: read response from chamber

        Return:
            False: Somehting went wrong
            Dictionary:
                state:   State of Response
                parm:    Setted parameter
                val:     Value of set
        """
        # initialize dictionary
        myParse = {}
        myParse['state'] = ""
        myParse['parm'] = ""
        myParse['val'] = ""
        # check for error reponse
        if ( False == msg ):
            print("Error: no message provided")
            return myParse
        # split at ':', f.e. OK:TEMP,S25
        msg = msg.split(':')        # OK:TEMP,S25 -> ['OK', 'TEMP,S25']
        myParse['state'] = msg[0]   # 'OK'
        msg = msg[1];               # 'TEMP,S25'
        # split at ',', f.e. 'TEMP,S25'
        msg = msg.split(',')        # 'TEMP,S25' -> ['TEMP', 'S25']
        i = 0;
        for elem in msg:
            if ( 0 == i ):
                myParse['parm'] = elem
            if ( 0 < i ):
                myParse['val'] = myParse['val'] + elem + ','
            i += 1
        # drop last ',' in 'val'
        myParse['val'] = myParse['val'][0:-1]
        # release parsed structure
        return myParse
    #*****************************
    
    
    #*****************************
    def is_numeric(self, msg):
        """
        Checks if message is numeric
        
        Return:
            False: not numric
            True:  numeric
        """
        # clean message
        msg = msg.strip()           # skip blanks
        msg = msg.replace('-', '')  # negativ number
        msg = msg.replace('+', '')  # positiv number
        msg = msg.replace('.', '')  # decimal point
        # check
        return msg.isnumeric()
    #*****************************   


    #*****************************
    def get_temp(self):
        """
        Get current temperature and temperature alarm configuration

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
        if ( False == self.chamber_write(espec_sh_def.CMD_GET_TEMP) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_GET_TEMP + "'")
            return False
        # Read Response, f.e. 26.4,0.0,140.0,-50.0
        rsp = self.chamber_read()
        # check for Error
        if ( False == rsp ):
            print("Error: Read Chamber")
            return False
        # check for error repsonse
        if ( True == espec_sh_def.RSP_FAIL in rsp ):
            print("Error: Response '" + rsp + "'")
            return False
        # initialize dictionary
        myVal = {}
        myVal['measured'] = ""
        myVal['setpoint'] = ""
        myVal['upalarm']  = ""
        myVal['lowalarm'] = ""
        # assign to dict
        i = 0
        for elem in rsp.split(','):
            # convert only if it's number
            if (True == self.is_numeric(elem)):
                conv = float(elem.strip())
            else:
                print(elem)
                conv = float('nan')
            # assign to dict
            if ( 0 == i ):
                myVal['measured'] = conv  # measured
            if ( 1 == i ):
                myVal['setpoint'] = conv  # set-point
            if ( 2 == i ):
                myVal['upalarm'] = conv   # tupper-limit-alarm-value
            if ( 3 == i ):
                myVal['lowalarm'] = conv  # lower-limit-alarm-value
            i+=1
        # return dict
        return myVal
    #*****************************
    
    
    #*****************************
    def get_humidity(self):
        """ Get current humidity and humidity alarm configuration
        
        Return:
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
        if ( False == self.chamber_write(espec_sh_def.CMD_GET_HUMI) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_GET_HUMI + "'")
            return False
        # Read Response, f.e. "25, 85, 100, 0"
        rsp = self.chamber_read()
        # check for error read
        if ( False == rsp ):
            print("Error: Read Chamber")
            return False
        # check for error repsonse
        if ( True == espec_sh_def.RSP_FAIL in rsp ):
            print("Error: Response '" + rsp + "'")
            return False
        # initialize dictionary
        myVal = {}
        myVal['measured'] = ""
        myVal['setpoint'] = ""
        myVal['upalarm']  = ""
        myVal['lowalarm'] = ""
        # assign to dict
        i = 0
        for elem in rsp.split(','):
            # convert only if it's number
            if (True == self.is_numeric(elem)):
                conv = float(elem.strip())
            else:
                conv = float('nan')
            # assign to dict
            if ( 0 == i ):
                myVal['measured'] = conv  # measured
            if ( 1 == i ):
                myVal['setpoint'] = conv  # set-point
            if ( 2 == i ):
                myVal['upalarm'] = conv   # upper-limit-alarm-value
            if ( 3 == i ):
                myVal['lowalarm'] = conv  # lower-limit-alarm-value
            i+=1
        # return dict
        return myVal
    #*****************************


    #*****************************
    def set_temp(self, temperature):
        """
        Set Chambers new temperature value

        Argument:
            Temperature: set temperature of chamber

        Return:
            False: Somehting went wrong
            True:  Temperature succesfull set
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
        if ( False == self.chamber_write(espec_sh_def.CMD_SET_TEMP + setTemp) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_SET_TEMP + setTemp + "'")
            return False
        # get response from chamber
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        if ( setRsp['state'] != espec_sh_def.RSP_OK ):
            print("Error: Set Temperature failed", setRsp)
            return False
        if ( setRsp['parm'] != "TEMP" ):
            print("Error: Response type '"+setRsp['parm']+"'")
            return False
        # Extract Temp
        getTemp = '{temp:.{frac}f}'.format(temp=float(setRsp['val'][1:]), frac=numDigits)   # S35 -> 35
        # check for set
        if ( getTemp != setTemp ):
            print("Error: Chamber not acknowledge new temperature set=" + setTemp + " ack=" + getTemp)
            return False
        # graceful end
        return True
    #*****************************


    #*****************************
    def set_power(self, pwr=espec_sh_def.PWR_OFF):
        """
        Enables Disables Power of climate chamber

        Argument:
            on:
                False: disable chamber
                True:  enable chamber

        Return
            False: Something went wrong
            True:  Action succesfull performed
        """
        # check if interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # check for argument
        if ( False == (pwr in (espec_sh_def.PWR_OFF, espec_sh_def.PWR_ON)) ):
            print("Error unsupported power mode'" + pwr + "'")
            return False
        # send command
        if ( False == self.chamber_write(espec_sh_def.CMD_SET_PWR+pwr) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_SET_PWR + pwr + "'")
            return False
        # get command response
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        # check for success
        if ( setRsp['state'] != espec_sh_def.RSP_OK ):
            print("Error: Set Temperature failed", setRsp)
            return False
        # check for correct class
        if ( setRsp['parm'] != espec_sh_def.CMD_SET_PWR.replace(',', '') ):
            print("Error: Response type '" + setRsp['parm'] + "'")
            return False
        # check for setting
        if ( setRsp['val'] != pwr ):
            print("Error: Mode setting failed, set='" + pwr + "' ack='" + setRsp['val'] + "'")
            return False
        # gracefull end
        return True
    #*****************************


    #*****************************
    def set_mode(self, mode=espec_sh_def.MODE_STANDBY):
        """
        Selects Chamber mode

        Argument:
            mode:   ( MODE_CONSTANT MODE_STANDBY MODE_OFF )

        Return
            False: Something went wrong
            True:  Action succesfull performed
        """
        # check if interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # check for argument
        if ( False == (mode in (espec_sh_def.MODE_CONSTANT, espec_sh_def.MODE_STANDBY, espec_sh_def.MODE_OFF)) ):
            print("Error unsupported operating mode '" + mode + "'")
            return False
        # send command
        if ( False == self.chamber_write(espec_sh_def.CMD_SET_MODE + mode) ):
            print("Error send command to chamber '" + espec_sh_def.CMD_SET_MODE + mode + "'")
            return False
        # get command response
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        # check for success
        if ( setRsp['state'] != espec_sh_def.RSP_OK ):
            print("Error: Set Mode Failed", setRsp)
            return False
        # check for correct class
        if ( setRsp['parm'] != espec_sh_def.CMD_SET_MODE.replace(',', '') ):
            print("Error: Response type '"+setRsp['parm']+"'")
            return False
        # check for setting
        if ( setRsp['val'] != mode ):
            print("Error: Mode setting failed, set='" + mode + "' ack='" + setRsp['val'] + "'")
            return False
        # gracefull end
        return True
    #*****************************


    #*****************************
    def start(self):
        """
        Starts temperature chamber

        Return
            False: Something went wrong
            True:  Succesfull
        """
        # check if serial interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # set temperature to 25°C
        if ( False == self.set_temp(25) ):
            return False
        # Power on
        if ( False == self.set_power(espec_sh_def.PWR_ON) ):
            return False
        # Set Mode to 'Constant'
        if ( False == self.set_mode(espec_sh_def.MODE_CONSTANT) ):
            return False
        # gracefull end
        return True
    #*****************************


    #*****************************
    def stop(self):
        """
        Stops Temperature chamber

        Return
            False: Something went wrong
            True:  Succesfull
        """
        # check if serial interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # set temperature to 25°C
        if ( False == self.set_temp(25) ):
            return False
        # Set Mode to 'Standby'
        if ( False == self.set_mode(espec_sh_def.MODE_STANDBY) ):
            return False
        # Power of
        if ( False == self.set_power(espec_sh_def.PWR_OFF) ):
            return False
        # gracefull end
        return True
    #*****************************

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':

    myChamber = especShSu(comPort="COM7")        # call class constructor
    myChamber.open()
    print("Temp ", myChamber.get_temp())
    print("Humi ", myChamber.get_humidity())
    myChamber.set_temp(25)
    myChamber.start()
    myChamber.stop()
    myChamber.close()
#------------------------------------------------------------------------------
