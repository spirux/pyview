#
#  ProgressWindowController.py
#  Pyview
#
#  Created by spirux on 21/04/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

import objc
from Foundation import *
from AppKit import *

class ProgressWindowController(NSWindowController):
	progressBar = objc.IBOutlet()
	messageLabel = objc.IBOutlet()
	
	def init(self):
		self = super(NSWindowController, self).init()
		NSBundle.loadNibNamed_owner_("ProgressSheet", self)
		return self
		
	def beginSheet(self, message, ownerWindow, minval=0.0, maxval=100.0, val=0.0):
		self.messageLabel.setStringValue_(message)
		self.progressBar.setMinValue_(minval)
		self.progressBar.setMaxValue_(maxval)
		self.progressBar.setDoubleValue_(val)
		NSApp().beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(self.window(), ownerWindow, self, None, 0)
		self.window().makeKeyWindow()
		
	def incrementBy_(self, amount):
		self.progressBar.incrementBy_(amount)
		#self.progressBar.displayIfNeeded() #It shows up fine without this!
		
	def safeIncrementBy_(self, amount):
		self.performSelectorOnMainThread_withObject_waitUntilDone_("incrementBy:", amount, False)
		
	def safeChangeMessage_(self, message):
		self.messageLabel.performSelectorOnMainThread_withObject_waitUntilDone_("setStringValue:", message, False)
		
	def end(self):
		NSApp().performSelectorOnMainThread_withObject_waitUntilDone_("endSheet:", self.window(), True)
		self.window().performSelectorOnMainThread_withObject_waitUntilDone_("orderOut:", self, True)

		
	
		
