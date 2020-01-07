# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2020
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          atwg_unittest.py
@date:          2020-01-07
@version:       0.1.0

@note           Unittest for ATWG.py
                  run ./test/unit/atwg_unittest.py
"""



#------------------------------------------------------------------------------
# Python Libs
#
import sys        # python path handling
import os         # platform independent paths
import unittest   # performs test
import math       # check nan

# Module libs
#
sys.path.append(os.path.abspath((os.path.dirname(os.path.abspath(__file__)) + "/../../")))  # add project root to lib search path
import ATWG                                                                                 # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class TestATWG(unittest.TestCase):

    #*****************************
    def setUp(self):
        """
        @note   set-ups test
        """
    #*****************************


    #*****************************
    def test_divide(self):
        pass
    #*****************************
    
    
    
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
