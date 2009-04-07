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
from OutlineViewDS import OutlineViewDS, WrapInOutlineViewItem
import ImageProxy

udir = lambda x: unicode(dir(x))

PVCInstance  = None;

class PyviewController(NSObject):
    biglabel = objc.IBOutlet()
    textField = objc.IBOutlet()
    imageView = objc.IBOutlet()
    outlineView = objc.IBOutlet()
                    
    def awakeFromNib(self):
        """
        Called when object is instantiated from NIB.
        Make instance globally available through PyviewController.PVCInstance. 
        """
        # Keep a reference of me in the PVCInstance to make
        # the controller from the NIB publicly accessible
        global PVCInstance
        PVCInstance = self
        
        # Create and connect a custom data source to the OutlineView
        # This enables python objects to be presentable through the OutlineView
        dataSource = OutlineViewDS.alloc().init()
        dataSource.root = []
        self.dataSource = dataSource
        dataSource.setSelectionCallback(lambda ip: self.change_image(ip))
        self.outlineView.setDelegate_(dataSource)
        self.outlineView.setDataSource_(dataSource)
        NSLog("I'm awake")
    
    @objc.IBAction
    def echo_(self,sender):
        self.load_images( (self.textField.stringValue(),) )

            
    def load_images(self, filenames):
        newitems = [WrapInOutlineViewItem(ImageProxy.ImageProxy(f)) for f in filenames]
        self.dataSource.root += newitems

        #inform the outline view  to reload everything
        #it is inefficient to update the whole view but I'm lazy
        self.outlineView.reloadItem_reloadChildren_(None, True)
        
        return self.change_image(newitems[0].payload)
        
    def change_image(self, imgProxy):
        filename = imgProxy.originalFileName
        try:
            image = AppKit.NSImage.alloc().initByReferencingFile_(filename)
			#image.initWithData()
            image.setBackgroundColor_(NSColor.blackColor())
            self.imageView.setImage_(image)
            
            #initialize text box with exif data
            strexif = unicode(imgProxy.human_readable_tags())
            self.biglabel.setString_(strexif)
            
            #set "address" string
            self.textField.setStringValue_(filename)
        except Exception, ex:
            print ex
        NSLog(u"Changed to filename: %s" % filename)

