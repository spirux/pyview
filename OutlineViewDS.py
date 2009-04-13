#
#  OutlineViewDS.py
#  Pyview
#
#  Created by spirux on 05/04/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

import objc
import AppKit
from Foundation import *

NSStringify = lambda s: NSString.alloc().initWithString_(s) 

class OutlineViewDS (NSObject):
	"""
	An adaptor class that allows a python tree to be the data source of an NSOutlineView
	"""
	def init(self):
		super(OutlineViewDS, self).init()
		self.root = None
		self.selection_callback = None
		#drag & drop pasteboard type
		self.dnd_type = "ImageProxy" 
		#we don't copy the dragged items in a pasteboard, but rather handle them internally
		self.dragged_items = None
		return self
	
	def setSelectionCallback(self, callback):
		self.selection_callback = callback

	def outlineView_numberOfChildrenOfItem_(self, view, item):
		if item is None:
			return len(self.root)
		return len(item.images)
			
	def outlineView_isItemExpandable_(self, view, item):
		if item is None:
			return True
		return item.isExpandable

	# Show expandable items in a different style
	def outlineView_isGroupItem_(self, view, item):
		return self.outlineView_isItemExpandable_(view, item)
	
	def outlineView_child_ofItem_(self, view, index, item):
		if item is None:
			return self.root[index]
		return item.images[index]
	
	def outlineView_objectValueForTableColumn_byItem_(self, view, tableColumn, item):
		attrib = str(tableColumn.identifier())
		value = getattr(item, attrib, "n/a")
		return NSStringify(str(value))

	def outlineView_shouldSelectItem_(self, view, item):
		"Notify our master that an item was selected"
		if self.selection_callback:
			self.selection_callback(item)
		return True
	
	def NSOutlineViewSelectionIsChangingNotification(self, sender):
		print "NSOutlineViewSelectionIsChangingNotification"
		
	def NSOutlineViewSelectionDidChangeNotification(self, sender):
		print "NSOutlineViewSelectionDidChangeNotification"
	
	#
	# Drag & Drop related data source functions
	#
	def outlineView_validateDrop_proposedItem_proposedChildIndex_(self, outlineView, info, target_item, index):
		return True
	
	def outlineView_writeItems_toPasteboard_(self, outlineView, items, pasteboard):
		#items come in an NSCFArray and that does not seem to be iterable
		self.dragged_items = []
		for i in xrange(len(items)):
			self.dragged_items.append(items[i])
		pasteboard.declareTypes_owner_([self.dnd_type], self)
		pasteboard.setData_forType_("", self.dnd_type)
		return True

	def outlineView_acceptDrop_item_childIndex_(self, outlineView, info, target_item, index):
		# resolve non group targets to their parents
		if target_item and not target_item.isExpandable:
			target_item = outlineView.parentForItem_(target_item)
			
		#find target list
		if target_item:
			target_list = target_item.images
		else:
			target_list = self.root

		# Check to make sure we don't allow a node to be inserted into one of its descendants!
		if any(is_descendent_of(i, target_item) for i in self.dragged_items):
			return False
			
		for item in reversed(self.dragged_items):
			#remove item from its previous parent
			parent = outlineView.parentForItem_(item)
			parent_list = self.root
			if parent:
				parent_list = parent.images
			#parent_list.remove(item)
			target_list.insert(index, item)

		outlineView.reloadItem_reloadChildren_(None, True)
		return True
		
	#
	# Helper functions
	#
def is_descendent_of(root, item):
	if (root is item) or (root.isExpandable and item in root.images):
		return True 
	elif root.isExpandable:
		return any(is_descendent_of(child, item) for child in root.images)
	return False