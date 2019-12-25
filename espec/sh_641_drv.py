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
        # Com interface
        self.interface = None   # init variable with open
        self.sim = None
        self.sim_rd = ""        # stores answer of next read request
        # managment flags
        self.isOpen = False;    # interface is open
        
        
        # todo, del
        self.com_port = float("nan")       # default is Com Port 1
        self.com_baudrate = float("nan")   # set baudrate
        self.com_databit = float("nan")    # data bits
        self.com_stopbit = float("nan")    # stop bits
        self.com_parity = ""

        # internal
        self.chamber_isOpen = False
        self.last_write_temp = float("nan") # stores last written value, used for reduction
    #*****************************


    #*****************************
    def open(self, cfgFile=None, simFile=None):
        """
        Opens COM port and try to recognize the climate chamber
        SRC: http://www.varesano.net/blog/fabio/serial%20rs232%20connections%20python
        """
        # Clima chamber interface mode
        if ( None == simFile ):
            # default interface config
            if ( None == cfgFile ):
                cfgFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + sh_const.IF_DFLT_CFG
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
            print("Enter simulation mode with dialog file '" + os.path.basename(simFile) + "'")
            # exists?
            if ( False == os.path.isfile(simFile) ):
                raise ValueError("Dialog file '" + simFile + "' not found") 
            # open file and load
            fH = open(simFile, 'r+')                            # open file for yaml loader
            self.sim = yaml.load(fH, Loader=yaml.FullLoader)    # load condig
            fH.close();                                         # close file handle        
        # mark interface/sim as open
        self.isOpen = True
        # try to indentify chamber
        self.write(sh_const.CMD_GET_TYPE)                   # request type
        chamberID = self.read()                             # read chamber repsonse
        if (False == (sh_const.RSP_CH_ID in chamberID) ):   # known type?
            raise ValueError("Error: Chamber '" + chamberID + "' unknown")
        # end
        return True
    #*****************************


    #*****************************
    def close(self):
        """
        Closes Handle
        """
        self.com.close()
        self.isOpen = False
    #*****************************


    #*****************************
    def write(self, msg):
        """
        Writes buffer to serial port or prepares answer for next read in case of sim
        """
        # interface open or sim mode?
        if ( False == self.isOpen ):
            raise ValueError("Interface nor sim mode used") 
        # prepare record answer
        if ( None != self.sim ):
            # make empty
            self.sim_rd = ""
            # request command
            if ("?" == msg[-1]):
                self.sim_rd = self.sim.get('req',{}).get(msg[:-1])  # add to next read buffer
            # set command, build ack message
            else:
                self.sim_rd = sh_const.RSP_OK + ":" + msg
        # pyhsical interface used
        else:
            # bring to line 
            msg += sh_const.MSC_LINE_END  # append termination
            self.com.write(msg.encode())  # write to com
        # all fine
        return True
    #*****************************


    #*****************************
    def read(self):
        """
        Reads from serial port into buffer

        Return:
            False:   Something went wrong
            String:  Response
        """
        # interface open or sim mode?
        if ( False == self.isOpen ):
            raise ValueError("Interface nor sim mode used")         
        # make empty
        msg = ""
        # prepare record answer
        if ( None != self.sim ):
            msg = self.sim_rd   # respond to previous request
            self.sim_rd = ""    # clear
        # pyhsical interface used
        else:
            # read from COM
            while ( False == (sh_const.MSC_LINE_END in msg) ):
                byte = self.com.read(1);
                msg += byte.decode()
            # drop line end and return
            msg = msg[:-len(sh_const.MSC_LINE_END)]     # skip CRNL
            msg = msg.strip()                           # remove leading/trailing blanks
        # all done
        return msg
    #*****************************


    #*****************************
    def parse(self, msg):
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
        # check for message
        if ( 0 == len(msg) ):
            raise ValueError("Empty message to parse provided")
        # dict
        myParse = {}
        # Set Command / Failed Request
        if ( -1 != msg.find(":") ):
            # split at ':', f.e. OK:TEMP,S25
            msg = msg.split(':')        # OK:TEMP,S25 -> ['OK', 'TEMP,S25']
            myParse['state'] = msg[0]   # 'OK'
            msg = msg[1];               # 'TEMP,S25'
            # split at ',', f.e. 'TEMP,S25'
            msg = msg.split(',')        # 'TEMP,S25' -> ['TEMP', 'S25']
            # iterate over list
            i = 0                       # helps to align
            myParse['parm'] = ""
            myParse['val'] = ""         # for recursive alignment
            for elem in msg:
                if ( 0 == i ):  myParse['parm'] = elem
                if ( 0 < i ):   myParse['val'] = myParse['val'] + elem + ','    # collect rest of param
                i += 1
            # drop last ',' in 'val'
            myParse['val'] = myParse['val'][0:-1]
        # measurement command
        else:
            # prepare dicts
            myParse['state'] = sh_const.RSP_OK  # 'OK'
            myParse['parm'] = "MEAS"            # measurement command was applied
            myMeas = {}                         # dict for measurment values
            myMeas['measured'] = float("nan")   # always full dict is returned
            myMeas['setpoint'] = float("nan")   #
            myMeas['upalarm']  = float("nan")   #
            myMeas['lowalarm'] = float("nan")   #
            # parse response
            i = 0
            for elem in msg.split(','):
                # non-numeric input, skip iteration
                if ( False == self.is_numeric(elem.strip()) ):
                    i+=1
                    continue
                # allign to dict
                if ( 0 == i ): myMeas['measured'] = float(elem.strip())                 # measured
                if ( 1 == i ): myMeas['setpoint'] = float(elem.strip())                 # set-point
                if ( 2 == i ): myMeas['upalarm'] = float(elem.strip())                  # upper-limit-alarm-value
                if ( 3 == i ): myMeas['lowalarm'] = float(elem.strip())                 # lower-limit-alarm-value                
                if ( 3 < i): raise ValueError("Unrecognized response in '" + msg + "'") # something went wrong
                i+=1
            # assign to reponse dict
            myParse['val'] = myMeas;
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
    def get_temperature(self):
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
        # request temperature from chamber
        try:
            self.write(sh_const.CMD_GET_TEMP)   #  write temperature request to chamber
            rsp = self.parse(self.read())       # read/parse
            if not ( (sh_const.RSP_OK == rsp['state']) and ("MEAS" == rsp['parm']) ):
                raise ValueError("Get temperaure request not succesfull completeted by chamber")
            myVal = rsp.get('val',{})           # extract temp values
        except:
            raise ValueError("Failed to get temperature not proper handled")
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
        # request humdity from chamber
        try:
            self.write(sh_const.CMD_GET_HUMI)   #  write temperature request to chamber
            rsp = self.parse(self.read())       # read/parse
            if not ( (sh_const.RSP_OK == rsp['state']) and ("MEAS" == rsp['parm']) ):
                raise ValueError("Get humidity request not succesfull completeted by chamber")
            myVal = rsp.get('val',{})           # extract humidity values
        except:
            raise ValueError("Get humidity request not proper handled")
        # return dict
        return myVal
    #*****************************


    #*****************************
    def set_temp(self, temperature=None):
        """
        Set Chambers new temperature value

        Argument:
            Temperature: set temperature of chamber

        Return:
            False: Something went wrong
            True:  Temperature successful set
        """
        # check for poper value
        if ( None == temperature ):
            return True
        # check if update is necessary
        if ( False == math.isnan(self.last_write_temp) ):
            if ( sh_const.MSC_TEMP_RESOLUTION >= abs(self.last_write_temp-temperature) ):
                return True
        # prepare       
        numDigs = len(str(sh_const.MSC_TEMP_RESOLUTION).split(".")[1])      # determine number of digits in fracs based on resulotion
        self.last_write_temp = temperature                                  # write only new value, if change is bigger then resulotion
        setTemp = '{temp:.{frac}f}'.format(temp=temperature, frac=numDigs)  # build temp string based  on chambers fraction settings
        # request chamber
        try:
            self.write(sh_const.CMD_SET_TEMP + setTemp)     # set new temperature
            rsp=self.parse(self.read())                     # read response from chamber
        except:
            raise ValueError("Request chamber failed")
        # check setting of new temperature
        #   rsp['val']: S35 -> 35
        if not ( (sh_const.RSP_OK == rsp['state']) and ("TEMP" == rsp['parm']) and (float(setTemp) == float(rsp['val'][1:])) ):
            raise ValueError("Failed to set new temperature")
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
        # check for proper arg
        if ( False == (pwr in (sh_const.PWR_OFF, sh_const.PWR_ON)) ):
            raise ValueError("unsupported power mode '" + pwr + "'")
        # request chamber
        try:
            self.write(sh_const.CMD_SET_PWR + pwr)  # set power state
            rsp=self.parse(self.read())             # read response from chamber
        except:
            raise ValueError("Request chamber failed")
        # check response
        if not ( (sh_const.RSP_OK == rsp['state']) and ("POWER" == rsp['parm']) and (pwr == rsp['val']) ):
            raise ValueError("Failed to set new power state")
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
        if ( False == self.write(sh_const.CMD_SET_MODE + mode) ):
            print("Error send command to chamber '" + sh_const.CMD_SET_MODE + mode + "'")
            return False
        # get command response
        setRsp = self.parse(self.read());   # read, and parse result
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

    myChamber = especShSu()                     # call class constructor
    myChamber.open()                            # open with interface defaults
    print("Temp: ", myChamber.get_temperature())
    print("Humi: ", myChamber.get_humidity())
    myChamber.set_temp(25)
    myChamber.start()
    myChamber.stop()
    myChamber.close()
#------------------------------------------------------------------------------
