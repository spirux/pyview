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

class OutlineViewItem (NSObject):
	def initWithPayload_(self, payload, expandable):
		self.payload = payload
		self.isExpandable = expandable
		return self

def WrapInOutlineViewItem(payload, expandable = False):
	return OutlineViewItem.alloc().initWithPayload_(payload, expandable)

class OutlineViewDS (NSObject):
	"""
	An adaptor class that allows a python tree to be the data source of an NSOutlineView
	"""
	
	def init(self):
		self.root = None
		self.selection_callback = None
		return self
	
	def setRoot(toplevelItems):
		"All items in the hierarchy MUST inherit from NSObject or risk memory corruption"
		self.root = toplevelItems
	
	def setSelectionCallback(self, callback):
		self.selection_callback = callback

	def outlineView_numberOfChildrenOfItem_(self, view, item):
		if item is None:
			return len(self.root)
		return len(item)
			
	def outlineView_isItemExpandable_(self, view, item):
		if item is None:
			return True
		return item.isExpandable
	
	def outlineView_child_ofItem_(self, view, index, item):
		if item is None:
			return self.root[index]
		return item[index]
	
	def outlineView_objectValueForTableColumn_byItem_(self, view, tableColumn, item):
		attrib = str(tableColumn.identifier())
		value = getattr(item.payload, attrib, "n/a")
		return NSStringify(str(value))

	def outlineView_shouldSelectItem_(self, view, item):
		"Notify our master that an item was selected"
		if self.selection_callback:
			self.selection_callback(item.payload)
		return True
