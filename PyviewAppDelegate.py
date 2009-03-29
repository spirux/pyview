#
#  PyviewAppDelegate.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

from Foundation import *
from AppKit import *

class PyviewAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
        
    def applicationOpenFile(self, filename):
        NSLog("Application did finish launching.")
        NSLog(filename)
    
    def applicationWillTerminate_(self,sender):
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
