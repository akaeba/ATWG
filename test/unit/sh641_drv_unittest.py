# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2019
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de
@status:        Development

@file:          sh641_drv_unittest.py
@date:          2019-12-22
@version:       0.1.0

@note           Unittest for sh641_drv.py
                  run ./test/unit/waves_unittest.py
"""



#------------------------------------------------------------------------------
import os                               # platform independent paths
import unittest                         # performs test
import espec.sh_641_drv as sh_641_drv   # Python Script under test
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class TestSh641(unittest.TestCase):
    
    #*****************************
    def setUp(self):
        """
        @note:  set-ups test
        """
    #*****************************
    
    
    #*****************************
    def test_open(self):
        drv = sh_641_drv.especShSu()                                                                        # create class
        drv.open(simFile = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "sh641_drv_dialog.yaml")  # open dialog file
    
    
    
    
    
    
    
    
    
    
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
