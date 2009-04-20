#
#  NSURLTransformer.py
#  Pyview
#
#  Created by spirux on 18/04/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *

class NSURLTransformer(NSValueTransformer):
	"""
	Transformer that allows saving/restoring paths in NSURLs as strings in the NSDefaults system.
	"""
	@staticmethod
	def transformedValueClass():
		return NSURL
	
	@staticmethod
	def allowsReverseTransformation():
		return True
	
	def transformedValue_(self, value):
		if value is None:
			return None
		return NSURL.alloc().initFileURLWithPath_(value)
	
	def reverseTransformedValue_(self, val):
		if val is None:
			return None
		return val.path()