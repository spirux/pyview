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

NSStringify = lambda s: NSString.stringWithString_(unicode(s)) 

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
		self.outlineView = None
		return self
	
	def setSelectionCallback(self, callback):
		self.selection_callback = callback
		
	def selectedItems(self):
		"""
		Returns all items currently selected. Convenience method.
		"""
		assert self.outlineView
		selection = self.outlineView.selectedRowIndexes()
		row = selection.firstIndex()
		selected = []
		while row != NSNotFound:
			selected.append(self.outlineView.itemAtRow_(row))
			#get next row index
			row = selection.indexGreaterThanIndex_(row)
		return selected
	
	def parentof(self, item):
		assert self.outlineView
		parent = self.outlineView.parentForItem_(item)
		if parent is None:
			parent = self.root
			assert item in parent
		return parent
		
	def parent_chain(self, item):
		if item is None:
			return []
		parent = self.outlineView.parentForItem_(item)
		return self.parent_chain(parent) + [parent]
		
	def closestCommonAncestor(self, items):
		assert self.outlineView
		#in case of no items, return None.
		if not items: return None
		chains = map(self.parent_chain, items)
		#find the common prefix
		prefix_len = common_prefix_length(chains)
		assert prefix_len >= 1 #all have the common parent "None"
		return chains[0][prefix_len - 1]
		
	def outlineView_numberOfChildrenOfItem_(self, view, item):
		#also keep a reference to the view that we are working with
		if not self.outlineView: self.outlineView = view
		if item is None:
			return len(self.root)
		return len(item)
			
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
		return item[index]
	
	def outlineView_objectValueForTableColumn_byItem_(self, view, tableColumn, item):
		attrib = str(tableColumn.identifier())
		value = getattr(item, attrib, "n/a")
		#for sets, we want a custom formatting of comma separated values
		if isinstance(value, set):
			value = u', '.join(value)
		return NSStringify(value)

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
	def outlineView_validateDrop_proposedItem_proposedChildIndex_(self, outlineView, info, target, index):
		return True
	
	def outlineView_writeItems_toPasteboard_(self, outlineView, items, pasteboard):
		#items come in an NSCFArray and that does not seem to be iterable
		self.dragged_items = []
		for i in xrange(len(items)):
			self.dragged_items.append(items[i])
		pasteboard.declareTypes_owner_([self.dnd_type], self)
		pasteboard.setData_forType_("", self.dnd_type)
		return True

	def outlineView_acceptDrop_item_childIndex_(self, outlineView, info, target, index):
		# resolve non group targets to their parents
		if target and not target.isExpandable:
			target = outlineView.parentForItem_(target)
			
		if target is None:
			target = self.root

		# Check to make sure we don't allow a node to be inserted into one of its descendants!
		if any(is_descendent_of(i, target) for i in self.dragged_items):
			return False
			
		for item in reversed(self.dragged_items):
			#remove item from its previous parent
			parent = outlineView.parentForItem_(item)
			if not parent: parent = self.root
			parent.remove(item)
			target.insert(index, item)

		outlineView.reloadItem_reloadChildren_(None, True)
		return True
		
		
	# Method needed to allow editing.
	def outlineView_setObjectValue_forTableColumn_byItem_(self, view, obj, columns, item):
		print "Setname called with", str(obj)
	#
	# Helper functions
	#
def is_descendent_of(root, item):
	if (root is item) or (root.isExpandable and item in root):
		return True 
	elif root.isExpandable:
		return any(is_descendent_of(child, item) for child in root)
	return False
	
def common_prefix_length(iterables):
	"""
	Returns the length of the common prefix of some iterables.
	"""
	shortest = min(map(len, iterables))
	
	for i in xrange(shortest):
		v = iterables[0][i]
		for x in iterables:
			if not x[i] is v:
				return i
	return shortest