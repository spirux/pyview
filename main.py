# -*- coding: utf-8 -*-
#
#  main.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

#import modules required by application
import objc
from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import PyviewAppDelegate
import PyviewController
import OutlineViewDS
import OpaqueView
import NSURLTransformer

# Verbose exception logging
objc.setVerbose(True)

# pass control to AppKit
AppHelper.runEventLoop()
