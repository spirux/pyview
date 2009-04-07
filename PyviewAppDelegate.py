#
#  PyviewAppDelegate.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

from Foundation import *
from AppKit import *
import PyviewController

class PyviewAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
        
    def application_openFiles_(self, app, filenames):
        NSLog("Application Open Files.")
        PyviewController.PVCInstance.load_images(filenames)
        app.replyToOpenOrPrint_(NSApplicationDelegateReplySuccess)
        
    @objc.IBAction
    def menuOpen_(self, sender):
        "Called on menu File > Open"
        dialog = NSOpenPanel.openPanel()
        
        # allow choosing both files and directories
        dialog.setCanChooseFiles_(True)
        dialog.setCanChooseDirectories_(True)
        
        if dialog.runModalForDirectory_file_(None, None) == NSOKButton:
            PyviewController.PVCInstance.load_images(dialog.filenames())
    
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
