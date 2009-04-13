#
#  OpaqueView.py
#  Pyview
#
#  Created by spirux on 07/04/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#
from AppKit import NSView, NSColor, NSRectFill
#from Foundation import *

class OpaqueView(NSView):

	def initWithFrame_(self, frame):
		self = super(OpaqueView, self).initWithFrame_(frame)
		if self:
			pass
		return self
		
	def isOpaque(self):
		return True
	
	def drawRect_(self, rect):
		# drawing a full black rectangle
		# set current drawing color
		NSColor.blackColor().set()
		#fill with black
		NSRectFill(rect)
	