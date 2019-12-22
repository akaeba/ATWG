# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          espec_corp_sh_641_drv.py
@date:          2019-07-23
@version:       0.1.0

@note           Provides basic functions to interface the climate chamber
                    * ESPEC CORP. SH-641


Pinning:
 * COM-Port
 * Table lists chamber site
     |--------+--------+----------------------------------+------+
     | Number | Signal | Remark                           | Used |
     |--------+--------+----------------------------------+------+
     |    1   | --     | Protective ground / cable shield | no   |
     |    2   | TXD    | Transmited data                  | yes  |
     |    3   | RXD    | Received data                    | yes  |
     |    4   | DSR    | Data set ready                   | yes  |
     |    5   | GND    | Signal ground                    | yes  |
     |    6   | DTR    | Data terminal ready              | yes  |
     |    7   | CTS    | Clear to send                    | yes  |
     |    8   | RTS    | Request to send                  | yes  |
     |    9   | --     | Ground                           | no   |
     |--------+--------+----------------------------------+------+     
"""



#------------------------------------------------------------------------------
import importlib.util               # submodule dependency check
import os                           # platform independent paths
import serial                       # COM port Interface
import math                         # required for isnan
import yaml                         # port config
import espec.sh_const as sh_const   # climate chamber defintions
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class especShSu:

    #*****************************
    def __init__(self):
        """
        Initialization of class
        """
        # Com port construct
        self.interface = None    # init variable with open
        self.sim = None
        
        
        self.com_port = float("nan")       # default is Com Port 1
        self.com_baudrate = float("nan")   # set baudrate
        self.com_databit = float("nan")    # data bits
        self.com_stopbit = float("nan")    # stop bits
        self.com_parity = ""
        # COM defaults
        self.config_com()
        # internal
        self.chamber_isOpen = False
        self.last_write_temp = float("nan") # stores last written value, used for reduction
    #*****************************
    
    
    #*****************************
    def config_com(self, port="COM1", baudrate=9600, databit=8, stopbit=1, parity="none"):
        """
        Configures COM port
            
        Arguments:
            port         Com Port
            baudrate     Baudrate
            databit      Databit count
            stopbit      Stopbit count
            parity       Databit parity
            
        Return:
            True:        all okay
        """
        # assign to internal
        self.com_port = port
        self.com_baudrate = baudrate
        self.com_databit = databit
        self.com_stopbit = stopbit
        self.com_parity = parity
        # done
        return True
    #*****************************
    


    #*****************************
    def check_dependency(self):
        """
        Checks if required packages are installed
        SRC: https://stackoverflow.com/questions/1051254/check-if-python-package-is-installed

        Return:
            True:   no dependency missing
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
    def open(self, cfg=None, sim=None):
        """
        Opens COM port and try to recognize the climate chamber
        SRC: http://www.varesano.net/blog/fabio/serial%20rs232%20connections%20python
        """
        # Clima chamber interface mode
        if ( None == sim ):
            # default interface config
            if ( None == cfg ):
                cfgFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + sh_const.IF_DFLT_CFG
            else:
                cfgFile = cfg;
            # check if file exists
            if ( False == os.path.isfile(cfgFile) ):
                raise ValueError("Interface configuration file '" + cfgFile + "' not found")
            # load interface config
            fH = open(cfgFile, 'r+')                                # open file for yaml loader
            self.interface = yaml.load(fH, Loader=yaml.FullLoader)  # load condig
            fH.close();                                             # close file handle
            # open interface
            #   https://pyserial.readthedocs.io/en/latest/
            self.com = serial.Serial(
                         port=self.interface.get('rs232',{}).get(os.name),  # port determined on os
                         baudrate=self.interface.get('baudrate'),           # current baudrate
                         stopbits=self.interface.get('stopbit'),
                         parity=self.interface.get('parity'),               # see 'serial.PARITY_NONE' for proper definition
                         bytesize=self.interface.get('databit'),
                         timeout=self.interface.get('tiout_sec')
                       ) 
        
        # simulation mode, Req/Res from file
        else:
            # User info
            print("Entered Simulation mode")
            
        
        
        
        
        
        
        #print(self.interface.get('rs232',{}).get(os.name))
        #print(self.interface)
        

        
        # todo
        return        
        
        
        # open COM interface
        if ( False == self.com.isOpen() ):
            print("Failed open COM interface ", str(self.com_port))
            return False
        # check Type
        if ( False == self.chamber_write(sh_const.CMD_GET_TYPE) ):
            print("Error: send command to chamber '" + sh_const.CMD_GET_TYPE + "'")
            return False
        chamberID = self.chamber_read()
        if ( False == chamberID ):
           print("Error: Get response '" + sh_const.CMD_GET_TYPE + "'")
           return False
        elif ( False == (sh_const.RSP_CH_ID in chamberID) ):
           print("Error: Chamber '" + chamberID + "' unknown")
           return False
        self.chamber_isOpen = True
        # graceful end
        return True
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
        msg += sh_const.MSC_LINE_END
        # check interface is open
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return False
        # write to com
        self.com.write(msg.encode())
        # graceful end
        return True
    #*****************************


    #*****************************
    def chamber_read(self):
        """
        Reads from serial port into buffer

        Return:
            False:   Something went wrong
            String:  Response
        """
        # check interface is open
        if ( False == self.com.isOpen() ):
            print("Serial Interface not open")
            return False
        # make empty
        msg = ""
        # read from COM
        while ( False == (sh_const.MSC_LINE_END in msg) ):
            byte = self.com.read(1);
            msg += byte.decode()
        # drop line end and return
        msg = msg[:-len(sh_const.MSC_LINE_END)]     # skip CRNL
        msg = msg.strip()                               # remove leading/trailing blanks
        return msg
    #*****************************


    #*****************************
    def parse_set_rsp(self, msg):
        """
        Parses response of set command

        Argument:
            msg: read response from chamber

        Return:
            False: Something went wrong
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
        # check for error response
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
            False: not numeric
            True:  numeric
        """
        # clean message
        msg = msg.replace(' ', '')  # remove blanks
        msg = msg.replace('-', '')  # negative number
        msg = msg.replace('+', '')  # positive number
        msg = msg.replace('.', '')  # decimal point
        # check
        return msg.isnumeric()
    #*****************************   


    #*****************************
    def get_temp(self):
        """
        Get current temperature and temperature alarm configuration

        Return
            False: Something went wrong
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
        if ( False == self.chamber_write(sh_const.CMD_GET_TEMP) ):
            print("Error: send command to chamber '" + sh_const.CMD_GET_TEMP + "'")
            return False
        # Read Response, f.e. 26.4,0.0,140.0,-50.0
        rsp = self.chamber_read()
        # check for Error
        if ( False == rsp ):
            print("Error: Read temperature from chamber")
            return False
        # check for error response
        if ( True == sh_const.RSP_FAIL in rsp ):
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
            # remove lead/trail blanks
            elem = elem.strip()
            # convert only if it's number
            if (True == self.is_numeric(elem)):
                conv = float(elem.strip())
            else:
                print(elem)
                conv = float("nan")
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
        """ 
        Get current humidity and humidity alarm configuration
        
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
        if ( False == self.chamber_write(sh_const.CMD_GET_HUMI) ):
            print("Error: Send command to chamber '" + sh_const.CMD_GET_HUMI + "'")
            return False
        # Read Response, f.e. "25, 85, 100, 0"
        rsp = self.chamber_read()
        # check for error read
        if ( False == rsp ):
            print("Error: Read Chamber")
            return False
        # check for error repsonse
        if ( True == sh_const.RSP_FAIL in rsp ):
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
            # remove lead/trail blanks
            elem = elem.strip()
            # convert only if it's number
            if (True == self.is_numeric(elem)):
                conv = float(elem.strip())
            else:
                conv = float("nan")
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
            False: Something went wrong
            True:  Temperature successful set
        """
        # check if interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # check if update is necessary
        if ( False == math.isnan(self.last_write_temp) ):
            if ( sh_const.MSC_TEMP_RESOLUTION >= abs(self.last_write_temp-temperature) ):
                return True
        # store last written temperature
        self.last_write_temp = temperature
        # prepare number string
        numDigits = len(str(sh_const.MSC_TEMP_RESOLUTION).split(".")[1])
        setTemp = '{temp:.{frac}f}'.format(temp=temperature, frac=numDigits)
        # send set temperature command
        if ( False == self.chamber_write(sh_const.CMD_SET_TEMP + setTemp) ):
            print("Error send command to chamber '" + sh_const.CMD_SET_TEMP + setTemp + "'")
            return False
        # get response from chamber
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        if ( setRsp['state'] != sh_const.RSP_OK ):
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
    def set_power(self, pwr=sh_const.PWR_OFF):
        """
        Enables Disables Power of climate chamber

        Argument:
            on:
                False: disable chamber
                True:  enable chamber

        Return
            False: Something went wrong
            True:  Action successful performed
        """
        # check if interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # check for argument
        if ( False == (pwr in (sh_const.PWR_OFF, sh_const.PWR_ON)) ):
            print("Error unsupported power mode'" + pwr + "'")
            return False
        # send command
        if ( False == self.chamber_write(sh_const.CMD_SET_PWR+pwr) ):
            print("Error send command to chamber '" + sh_const.CMD_SET_PWR + pwr + "'")
            return False
        # get command response
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        # check for success
        if ( setRsp['state'] != sh_const.RSP_OK ):
            print("Error: Set Temperature failed", setRsp)
            return False
        # check for correct class
        if ( setRsp['parm'] != sh_const.CMD_SET_PWR.replace(',', '') ):
            print("Error: Response type '" + setRsp['parm'] + "'")
            return False
        # check for setting
        if ( setRsp['val'] != pwr ):
            print("Error: Mode setting failed, set='" + pwr + "' ack='" + setRsp['val'] + "'")
            return False
        # graceful end
        return True
    #*****************************


    #*****************************
    def set_mode(self, mode=sh_const.MODE_STANDBY):
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
        if ( False == (mode in (sh_const.MODE_CONSTANT, sh_const.MODE_STANDBY, sh_const.MODE_OFF)) ):
            print("Error unsupported operating mode '" + mode + "'")
            return False
        # send command
        if ( False == self.chamber_write(sh_const.CMD_SET_MODE + mode) ):
            print("Error send command to chamber '" + sh_const.CMD_SET_MODE + mode + "'")
            return False
        # get command response
        setRsp = self.parse_set_rsp(self.chamber_read());   # read, and parse result
        # check for success
        if ( setRsp['state'] != sh_const.RSP_OK ):
            print("Error: Set Mode Failed", setRsp)
            return False
        # check for correct class
        if ( setRsp['parm'] != sh_const.CMD_SET_MODE.replace(',', '') ):
            print("Error: Response type '"+setRsp['parm']+"'")
            return False
        # check for setting
        if ( setRsp['val'] != mode ):
            print("Error: Mode setting failed, set='" + mode + "' ack='" + setRsp['val'] + "'")
            return False
        # graceful end
        return True
    #*****************************


    #*****************************
    def start(self):
        """
        Starts temperature chamber

        Return
            False: Something went wrong
            True:  Successful
        """
        # check if serial interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # set temperature to 25°C
        if ( False == self.set_temp(25) ):
            return False
        # Power on
        if ( False == self.set_power(sh_const.PWR_ON) ):
            return False
        # Set Mode to 'Constant'
        if ( False == self.set_mode(sh_const.MODE_CONSTANT) ):
            return False
        # graceful end
        return True
    #*****************************


    #*****************************
    def stop(self):
        """
        Stops Temperature chamber

        Return
            False: Something went wrong
            True:  Successful
        """
        # check if serial interface is open
        if ( False == self.chamber_isOpen ):
            return False
        # set temperature to 25°C
        if ( False == self.set_temp(25) ):
            return False
        # Set Mode to 'Standby'
        if ( False == self.set_mode(sh_const.MODE_STANDBY) ):
            return False
        # Power of
        if ( False == self.set_power(sh_const.PWR_OFF) ):
            return False
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def get_resolution_fracs(self):
        """
        Returns Humidity and Temperature resolution in fracs
        """
        # initialize dictionary
        fracs = {}
        fracs['temperature'] = 1
        fracs['humidity'] = 1
        return fracs
    #***************************** 
        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':

    myChamber = especShSu()            # call class constructor
    myChamber.config_com(port="COM7")  # configure IF
    myChamber.open()
    print("Temp: ", myChamber.get_temp())
    print("Humi: ", myChamber.get_humidity())
    myChamber.set_temp(25)
    myChamber.start()
    myChamber.stop()
    myChamber.close()
#------------------------------------------------------------------------------
