# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          sh641.py
@date:          2019-07-23

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
import os                  # platform independent paths
import serial              # COM port Interface
import math                # required for isnan
import yaml                # port config
from . import sh641Const   # ESPEC SH641 constants
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
        # internal
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
                cfgFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + sh641Const.IF_DFLT_CFG
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
                         port=self.interface['rs232'][os.name],     # port determined on os
                         baudrate=self.interface['baudrate'],       # current baudrate
                         stopbits=self.interface['stopbit'],
                         parity=self.interface['parity'],           # see 'serial.PARITY_NONE' for proper definition
                         bytesize=self.interface['databit'],
                         timeout=self.interface['tiout_sec']
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
        self.write(sh641Const.CMD_GET_TYPE)                 # request type
        chamberID = self.read()                             # read chamber repsonse
        if (False == (sh641Const.RSP_CH_ID in chamberID) ): # known type?
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
        @note           Writes buffer to serial port or prepares answer for next read in case of sim
        
        @param msg      command for chamber
        @rtype          boolean
        @return         if succesfull
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
                self.sim_rd = self.sim['req'][msg[:-1]]     # add to next read buffer
            # set command, build ack message
            else:
                self.sim_rd = sh641Const.RSP_OK + ":" + msg
        # pyhsical interface used
        else:
            # bring to line 
            msg += sh641Const.MSC_LINE_END # append termination
            self.com.write(msg.encode())   # write to com
        # all fine
        return True
    #*****************************


    #*****************************
    def read(self):
        """
        @note           reads from serial port into buffer
        
        @rtype          string
        @return         chamber reponse in ASCII text
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
            while ( False == (sh641Const.MSC_LINE_END in msg) ):
                byte = self.com.read(1);
                msg += byte.decode()
            # drop line end and return
            msg = msg[:-len(sh641Const.MSC_LINE_END)]   # skip CRNL
            msg = msg.strip()                           # remove leading/trailing blanks
        # all done
        return msg
    #*****************************


    #*****************************
    def parse(self, msg):
        """
        @note           parses chamber responses
                          * set command
                          * get command
                          
        @param msg      chamber response string
        @type           string
        @rtype          dict
        @return         {'state': , 'parm': , 'val', :} in case of measuement
                        command contents contents val a dict
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
            myParse['state'] = sh641Const.RSP_OK    # 'OK'
            myParse['parm'] = "MEAS"                # measurement command was applied
            myMeas = {}                             # dict for measurment values
            myMeas['measured'] = float("nan")       # always full dict is returned
            myMeas['setpoint'] = float("nan")       #
            myMeas['upalarm']  = float("nan")       #
            myMeas['lowalarm'] = float("nan")       #
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
        @note           checks if input string is a numeric value
        
        @rtype          boolean
        @return         true if input is numeric
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
    def get_clima(self):
        """
        @note           Current measured clima
        
        @rtype          dict
        @return         humidity/temperature vals
        """
        # init resut
        clima = {'temperature': float('nan'), 'humidity': float('nan')}
        # acquire temperature
        try:
            self.write(sh641Const.CMD_GET_TEMP)             # write temperature request to chamber
            rsp = self.parse(self.read())                   # read/parse; dict: measured, setpoint, upalarm, lowalarm
            if not ( (sh641Const.RSP_OK == rsp['state']) and ("MEAS" == rsp['parm']) ):
                raise ValueError("Get temperaure request not succesfull completeted by chamber")
            clima['temperature'] = rsp['val']['measured']   # extract current temp values
        except:
            raise ValueError("Failed to get temperature not proper handled")
        # acquire humidity
        try:
            self.write(sh641Const.CMD_GET_HUMI)         #  write temperature request to chamber
            rsp = self.parse(self.read())               # read/parse; dict: measured, setpoint, upalarm, lowalarm
            if not ( (sh641Const.RSP_OK == rsp['state']) and ("MEAS" == rsp['parm']) ):
                raise ValueError("Get humidity request not succesfull completeted by chamber")
            clima['humidity'] = rsp['val']['measured']  # extract humidity values
        except:
            raise ValueError("Get humidity request not proper handled")        
        # release result
        return clima
    #*****************************


    #*****************************
    def set_clima(self, clima=None):
        """
        @note           set chambers new clima value
                          * temperature
                          
        @param clima    new clima value
        @type           dict, {'temperature': myVal}
        @rtype          boolean
        @return         successful
        """
        # check for arg
        if ( clima == None ):
            raise ValueError("No new data provided")
        # try to set temperature
        try:
            # check if update is necessary
            if ( False == math.isnan(self.last_write_temp) ):
                if ( sh641Const.MSC_TEMP_RESOLUTION >= abs(self.last_write_temp-clima['temperature']) ):
                    return True
            # prepare       
            numDigs = len(str(sh641Const.MSC_TEMP_RESOLUTION).split(".")[1])            # determine number of digits in fracs based on resulotion
            self.last_write_temp = clima['temperature']                                 # write only new value, if change is bigger then resulotion
            setTemp = '{temp:.{frac}f}'.format(temp=clima['temperature'], frac=numDigs) # build temp string based  on chambers fraction settings
            # request chamber
            try:
                self.write(sh641Const.CMD_SET_TEMP + setTemp)   # set new temperature
                rsp=self.parse(self.read())                     # read response from chamber
            except:
                raise ValueError("Request chamber failed")
            # check setting of new temperature
            #   rsp['val']: S35 -> 35
            if not ( (sh641Const.RSP_OK == rsp['state']) and ("TEMP" == rsp['parm']) and (float(setTemp) == float(rsp['val'][1:])) ):
                raise Warning("Temperature set check failed")
        except:
            raise ValueError("Failed to set clima")
        # graceful end
        return True
    #*****************************


    #*****************************
    def set_power(self, pwr=sh641Const.PWR_OFF):
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
        if ( False == (pwr in (sh641Const.PWR_OFF, sh641Const.PWR_ON)) ):
            raise ValueError("unsupported power mode '" + pwr + "'")
        # request chamber
        try:
            self.write(sh641Const.CMD_SET_PWR + pwr)    # set power state
            rsp=self.parse(self.read())                 # read response from chamber
        except:
            raise ValueError("Request chamber failed")
        # check response
        if not ( (sh641Const.RSP_OK == rsp['state']) and ("POWER" == rsp['parm']) and (pwr == rsp['val']) ):
            raise ValueError("Failed to set new power state")
        # graceful end
        return True
    #*****************************


    #*****************************
    def set_mode(self, mode=sh641Const.MODE_STANDBY):
        """
        Selects Chamber mode

        Argument:
            mode:   ( MODE_CONSTANT MODE_STANDBY MODE_OFF )

        Return
            False: Something went wrong
            True:  Action succesfull performed
        """
        # check for proper arg
        if ( False == (mode in (sh641Const.MODE_CONSTANT, sh641Const.MODE_STANDBY, sh641Const.MODE_OFF)) ):
            raise ValueError("unsupported operating mode '" + mode + "'")
        # request chamber
        try:
            self.write(sh641Const.CMD_SET_MODE + mode)  # set mode
            rsp=self.parse(self.read())                 # read response from chamber
        except:
            raise ValueError("Request chamber failed")
        # check response
        if not ( (sh641Const.RSP_OK == rsp['state']) and ("MODE" == rsp['parm']) and (mode == rsp['val']) ):
            raise ValueError("Failed to set new mode")
        # graceful end
        return True        
    #*****************************


    #*****************************
    def start(self, temperature=None):
        """
        Starts temperature chamber

        Return
            False: Something went wrong
            True:  Successful
        """
        # check if start temp provided, othweise use chambers current temperature
        if ( None == temperature ):
            temperature = self.get_clima()['temperature']
        # start chamber
        try:
            self.set_clima(clima={'temperature': temperature})  # set start temp
            self.set_power(sh641Const.PWR_ON)                   # enable chamber
            self.set_mode(sh641Const.MODE_CONSTANT)             # run in constant mode
        except:
            raise ValueError("Failed to start chamber")
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
        # stop chamber
        try:
            self.set_mode(sh641Const.MODE_STANDBY)  # bring to standby
            self.set_power(sh641Const.PWR_OFF)      # disable
        except:
            raise ValueError("Failed to stop chamber")
        # graceful end
        return True
    #*****************************
    
    
    #*****************************
    def info(self):
        """
        Returns Humidity and Temperature resolution in fracs
        """
        # build fracs dict
        fracs = {}
        fracs['temperature'] = 1   # temperature frac digits
        fracs['humidity'] = 1      # humidity frac digits
        # build final info structure
        info = {}
        info['fracs'] = fracs           # add
        info['name'] = "ESPEC_SH641"    # insert
        # release
        return info
    #***************************** 
        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':

    myChamber = especShSu()                         # call class constructor
    myChamber.open()                                # open with interface defaults
    print(myChamber.get_clima())                    # get current clima
    myChamber.start()                               # start chamber
    myChamber.set_clima(clima={'temperature': 25})  # set temperature value
    myChamber.stop()                                # stop chamber
    myChamber.close()                               # close handle
#------------------------------------------------------------------------------
