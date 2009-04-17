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
from datetime import datetime, timedelta
from OutlineViewDS import *
from os.path import isdir

import ImageProxy

PVCInstance  = None;

class PyviewController(NSObject):
    exifLabel = objc.IBOutlet()
    exifPanel = objc.IBOutlet()
    imageView = objc.IBOutlet()
    outlineView = objc.IBOutlet()
    dataSource = objc.IBOutlet()
    window = objc.IBOutlet()
    
    def awakeFromNib(self):
        """
        Called when object is instantiated from NIB.
        Make instance globally available through PyviewController.PVCInstance. 
        """
        # Keep a reference of me in the PVCInstance to make
        # the controller from the NIB publicly accessible
        global PVCInstance
        PVCInstance = self
        
        self.dataSource.root = []
        # when an item gets selected from the ones in our datasource 
        # change_image is called to change the currently selected image
        selected_callback = lambda item: self.change_image(item)
        self.dataSource.setSelectionCallback(selected_callback)
        #load our logo
        self.logoimg = NSBundle.mainBundle().pathForResource_ofType_("exificon", "icns")
        self.show_image_from_path(self.logoimg)
        
        # Don't allow the exif panel to steal focus
        self.exifPanel.setBecomesKeyOnlyIfNeeded_(True)
        # set-up drag & drop
        self.outlineView.registerForDraggedTypes_(["ImageProxy"])
        self.window.registerForDraggedTypes_([NSFilenamesPboardType])
        self.dragged_files = None
            
    def load_images(self, filenames):
        #TODO: handle directories by descending recursively
        newitems = []
        for fname in filenames:
            img = ImageProxy.ImageProxy.alloc().init()
            img.__init__(fname)
            newitems.append(img)
        self.dataSource.root += newitems
        
        #a.performSelector_withObject_afterDelay_(<#aSelector#>, <#anArgument#>, <#delay#>)

        #inform the outline view  to reload everything
        #it is inefficient to update the whole view but I'm lazy
        self.outlineView.reloadItem_reloadChildren_(None, True)
        if newitems:
            self.change_image(newitems[0])
        
    def show_image_from_path(self, filepath):
        url = NSURL.fileURLWithPath_(filepath)
        self.imageView.setImageWithURL_(url)
    
    def change_image(self, imgProxy):
        try:
            filename = imgProxy.originalFileName
            #show image
            self.show_image_from_path(filename)
            #initialize text box with exif data
            strexif = unicode(imgProxy.human_readable_tags())
            self.exifLabel.setString_(strexif)
            NSLog(u"Changed to filename: %s" % filename)
        except Exception, ex:
            print ex, "With imgProxy:", imgProxy


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
        types = ('jpg', 'JPG', 'jpeg', 'JPEG')
        if dialog.runModalForDirectory_file_types_(None, None, types) == NSOKButton:
            self.load_images(dialog.filenames())

    @objc.IBAction
    def toggleExifPanel_(self, sender):
        if self.exifPanel.isVisible():
            self.exifPanel.orderOut_(self)
        else:
            self.exifPanel.orderFront_(self)

    @objc.IBAction
    def removeSelected_(self, sender):
        modified = set()
        
        for item in self.dataSource.selectedItems():
            parent = self.outlineView.parentForItem_(item)
            modified.add(parent)
            if parent is None:
                parent = self.dataSource.root
            parent.remove(item)

        for parent in modified:
            self.outlineView.reloadItem_reloadChildren_(parent, True)
    
    @objc.IBAction
    def groupSelected_(self, sender):
        selected = self.dataSource.selectedItems()
        # We will hang the new group under the closest ancestor
        common_parent = self.dataSource.closestCommonAncestor(selected)
        if common_parent is None:
            common_parent = self.dataSource.root
        
        #unlink all selected items
        for item in selected:
            parent = self.dataSource.parentof(item)
            parent.remove(item)
            
        newgroup = PhotoSessionFactory()
        for o in selected:
            newgroup.append(o)
        common_parent.append(newgroup)
        self.outlineView.reloadItem_reloadChildren_(None, True)


    @objc.IBAction
    def ungroupSelected_(self, sender):
        selected = self.dataSource.selectedItems()

        #work only with photosessions
        isphotosession = lambda x: isinstance(x, ImageProxy.PhotoSession)
        selected = filter(isphotosession, selected)
        #find out the parent of everyone
        parents = {}
        for group in selected:
            parents[group] = self.dataSource.parentof(group)

        #move images to parents
        for group in selected:
            parent = parents[group]
            for image in group.images:
                parent.append(image)
        
        #unlink the removed groups
        for group in selected:
            parents[group].remove(group)
        
        self.outlineView.reloadItem_reloadChildren_(None, True)

    
    @objc.IBAction
    def autogroupItems_(self, sender):
        hours5 = timedelta(0, 5*3600, 0)
        insession = lambda img, ses: ImageProxy.by_day(img, ses, hours5)
        clustered = ImageProxy.cluster_images(self.dataSource.root, insession, PhotoSessionFactory)
        self.dataSource.root = clustered
        self.outlineView.reloadItem_reloadChildren_(None, True)
        
    @objc.IBAction
    def storeImageHierarchy_(self, sender):
        a = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(u"Not implemented", None, None, None, u"This function is  not implemented yet.")
        a.runModal()
    
    ################################################
    # Drag & Drop support
    ################################################
    def draggingEntered_(self, sender):
    	pasteboard = sender.draggingPasteboard()
        if not pasteboard.types().containsObject_(NSFilenamesPboardType):
            return NSDragOperationNone
        fnames = pasteboard.propertyListForType_(NSFilenamesPboardType)
        # accept all supported images and directories
        is_loadable = lambda x: ImageProxy.isLoadableFileType(x) or isdir(x)

        if all(is_loadable(f) for f in fnames):
            self.dragged_files = fnames
            return NSDragOperationCopy

        return NSDragOperationNone
        
    def draggingExited_(self, sender):
        self.dragged_files = None
        print "Oh, you changed your mind. It's OK."
    
    def performDragOperation_(self, sender):
        if self.dragged_files:
            self.load_images(self.dragged_files)
            return True
        return False
    
def PhotoSessionFactory():
    ps = ImageProxy.PhotoSession.alloc().init()
    ps.__init__()
    return ps
