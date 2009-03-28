#
#  PyviewController.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

import objc
import AppKit
from Foundation import *
udir = lambda x: unicode(dir(x))

class PyviewController(NSObject):        
    textField = objc.IBOutlet()
    textlabel = objc.IBOutlet()
    imageView = objc.IBOutlet()
    
    @objc.IBAction
    def echo_(self,sender):
        search_value = self.textField.stringValue()
        #NSLog(unicode(dir(self.textlabel)))
        #print udir(self.imageView.image)
        #print type(self.imageView.image)
        try:
            image = AppKit.NSImage.alloc().initByReferencingFile_(search_value)
            self.imageView.setImage_(image)
        except Exception, ex:
            print ex
        self.textlabel.setStringValue_(u"-" + search_value + u"-")
        NSLog(u"Search: %s" % search_value)

