#
#  PyviewAppDelegate.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

from Foundation import *
from AppKit import *
import objc
import PyviewController
from Preferences import Preferences

class PyviewAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        self.preferences = Preferences.alloc().init()
        NSLog("Application did finish launching.")
        
    def application_openFiles_(self, app, filenames):
        NSLog("Application Open Files.")
        PyviewController.PVCInstance.load_images_(filenames)
        app.replyToOpenOrPrint_(NSApplicationDelegateReplySuccess)
    
    def applicationWillTerminate_(self, sender):
        NSLog("Application will terminate.")

    def applicationSupportFolder(self):
        paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
        basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
        fullPath = basePath.stringByAppendingPathComponent_("MetaWindow")
        if not os.path.exists(fullPath):
            os.mkdir(fullPath)
        return fullPath
            
    def pathForFilename(self,filename):
        return self.applicationSupportFolder().stringByAppendingPathComponent_(filename)
        
    def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
        return True

    @objc.IBAction
    def showPreferences_(self, sender):
        preferences = self.preferences
        w = preferences.window()
        w.makeKeyAndOrderFront_(self)
        