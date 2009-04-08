#
#  PyviewController.py
#  Pyview
#
#  Created by spirux on 23/03/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

import objc
from AppKit import *
from Foundation import *
from os.path import basename
from OutlineViewDS import OutlineViewDS, WrapInOutlineViewItem
import ImageProxy

PVCInstance  = None;

class PyviewController(NSObject):
    exifLabel = objc.IBOutlet()
    exifPanel = objc.IBOutlet()
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
        
        # Don't allow the exif panel to steal focus
        self.exifPanel.setBecomesKeyOnlyIfNeeded_(True)
        
        NSLog("I'm awake")
            
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
            image = NSImage.alloc().initByReferencingFile_(filename)
			#image.initWithData()
            image.setBackgroundColor_(NSColor.blackColor())
            self.imageView.setImage_(image)
            
            #initialize text box with exif data
            strexif = unicode(imgProxy.human_readable_tags())
            self.exifLabel.setString_(strexif)
        except Exception, ex:
            print ex
        NSLog(u"Changed to filename: %s" % filename)

    @objc.IBAction
    def menuOpen_(self, sender):
        "Called on menu File > Open"
        dialog = NSOpenPanel.openPanel()
        
        dialog.setResolvesAliases_(True)
        dialog.setAllowsMultipleSelection_(True)
        
        # allow choosing both files and directories
        dialog.setCanChooseFiles_(True)
        dialog.setCanChooseDirectories_(True)
        
        #allowed file types
        types = ('jpg', 'JPEG')
        if dialog.runModalForDirectory_file_types_(None, None, types) == NSOKButton:
            self.load_images(dialog.filenames())


    @objc.IBAction
    def toggleExifPanel_(self, sender):
        if self.exifPanel.isVisible():
            self.exifPanel.orderOut_(self)
        else:
            self.exifPanel.orderFront_(self)
