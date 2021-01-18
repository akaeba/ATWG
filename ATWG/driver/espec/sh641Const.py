# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          sh641Const.py
@date:          2019-12-21

@brief:         ESPEC CORP. SH-641 Command Strings
@see:           https://www.atecorp.com/atecorp/media/pdfs/data-sheets/espec-sh-641_datasheet.pdf
"""


# Commands
CMD_GET_TYPE="TYPE?"        # request chamber identification
CMD_GET_TEMP="TEMP?"        # request chamber temperature
CMD_SET_TEMP="TEMP,S"       # chamber temperature set point
CMD_SET_TEMP_ALUP="TEMP,H"  # chamber alarm upper temperature
CMD_SET_TEMP_ALLOW="TEMP,L" # chamber alarm lower temperature
CMD_SET_PWR="POWER,"        # chamber power on
PWR_ON="ON"                 # chamber switch on
PWR_OFF="OFF"               # chamber switch off
CMD_SET_MODE="MODE,"        # chamber mode command
MODE_CONSTANT="CONSTANT"    # constant temperature mode
MODE_STANDBY="STANDBY"      # chamber in standby, no temperature set
MODE_OFF="OFF"              # disables panel
CMD_GET_HUMI="HUMI?"        # request chamber humidity

# Responses
RSP_CH_ID="T,T,S2,160.0"    # ID of chamber
RSP_OK="OK"                 # Chamber accepts command
RSP_FAIL="NA"               # chamber discards command

# Misc
MSC_LINE_END="\r\n"         # used line end
MSC_TIOUT_RS232_MSEC=10e3   # Time out for serial read
MSC_TEMP_RESOLUTION=0.1     # Resolution temperature chamber

# Interface Defaults
IF_DFLT_CFG="sh641InterfaceDefault.yml"

# Ratings
TEMP_MAX_C=150          # Chamber maximum temperature in celsius
TEMP_MIN_C=-40          # Chambers minimal temperature in celsius
TEMP_GRAD_RISE=2.9      # chambers heating rate in celsius/minute
TEMP_GRAD_FALL=-1.7     # chambers cooling rate in celsius/minute
