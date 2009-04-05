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
from os.path import basename
import ImageProxy
udir = lambda x: unicode(dir(x))

PVCInstance  = None;

class PyviewController(NSObject):
    biglabel = objc.IBOutlet()
    textField = objc.IBOutlet()
    imageView = objc.IBOutlet()
    
    @objc.IBAction
    def echo_(self,sender):
        self.change_image(self.textField.stringValue())
                
    def awakeFromNib(self):
        """
        Called when object is instantiated from NIB.
        Make instance globally available through PyviewController.PVCInstance. 
        """
        global PVCInstance
        assert not PVCInstance
        PVCInstance = self
        NSLog("I'm awake")
        
    def load_images(self, filenames):
        return self.change_image(filenames[0])
        
    def change_image(self, filename):
        try:
            image = AppKit.NSImage.alloc().initByReferencingFile_(filename)
			#image.initWithData()
            self.imageView.setImage_(image)
            self.show_exif(filename)
            self.textField.setStringValue_(filename)
        except Exception, ex:
            print ex
        #self.textlabel.setStringValue_(u"-" + basename(filename) + u"-")
        NSLog(u"Changed to filename: %s" % filename)
    
    def show_exif(self, filename):
        ip = ImageProxy.ImageProxy(filename)
        #NSLog(udir(self.biglabel))
        #self.biglabel.selectAll_(self)
        tstorage = self.biglabel#.textStorage
        tstorage.setString_(unicode(ip.human_readable_tags()))

            
