#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Definitions for Command/Response Strings
 * ESPEC CORP. SH-641
"""

__FILE__        = "espec_sh_def.py"
__author__ 		= "Andreas Kaeberlein"
__copyright__ 	= "Copyright 2018, Arbitrary Temperature Waveform Generator"
__credits__     = ["AKAE"]

__license__ 	= "LGPLv3"
__version__ 	= "0.1.0"
__maintainer__ 	= "Andreas Kaeberlein"
__email__ 		= "andreas.kaeberlein@web.de"
__status__ 		= "Development"


# Commands
CMD_GET_TYPE="TYPE?"             # request chamber identification
CMD_GET_TEMP="TEMP?"             # request chamber temperature
CMD_SET_TEMP="TEMP,S"            # chamber temperature set point
CMD_SET_TEMP_ALUP="TEMP,H"       # chamber alarm upper temperature
CMD_SET_TEMP_ALLOW="TEMP,L"      # chamber alarm lower temperature

# Responses
RSP_CH_ID="T,T,S2,160.0"         # ID of chamber

# Misc
MSC_LINE_END="\r\n"              # used line end
MSC_ERO_CMD="NA:COMMAND ERR"     # Command error
MSC_ERO_PRM="NA:PARAMETER ERR"   # Parameter Error
MSC_TIOUT_SERRD_MSEC=10e3        # Time out for serial read
MSC_TEMP_RESOLUTION=0.1          # Resolution tmperature chamber
