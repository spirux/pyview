#
#  main.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit
from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import PyviewAppDelegate
import PyviewController
import OutlineViewDS
import OpaqueView

# pass control to AppKit
AppHelper.runEventLoop()
