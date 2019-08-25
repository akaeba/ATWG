# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          waves_unittest.py
@date:          2019-08-25
@version:       0.1.0

@note           Unittest for waves.py
"""



#------------------------------------------------------------------------------
import unittest         # performs test
import math             # check nan
from src import waves   # Python Script under test
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
class TestWaves(unittest.TestCase):
    
    #*****************************
    def setUp(self):
        """
        @note:  set-ups test
        """
        self.dut = waves    # create object under test
    #*****************************
    
    
    #*****************************
    def test_divide(self):
        """
        @note:  tests zero divide divider function
        """
        self.assertEqual(self.dut.waves.divide(self=self.dut, dividend=1, divisor=2), 0.5)          # check normal division
        self.assertTrue(math.isnan(self.dut.waves.divide(self=self.dut, dividend=1, divisor=0)))    # check divide by zero
    #*****************************

        
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
