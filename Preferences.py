#
#  Preferences.py
#  Pyview
#
#  Created by spirux on 19/04/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

from Foundation import *
from AppKit import *
import objc

sharedInstance = None

class Preferences(NSWindowController):	
	def init(self):
		"There must be only one instance of preferences."
		global 	sharedInstance
		if sharedInstance:
			self.release()
		else:
			self = super(Preferences, self).initWithWindowNibName_("PreferencesWindow")
			sharedInstance = self
		return sharedInstance
	
	def dealloc(self):
		if not self is sharedInstance:
			super(Preferences, self).dealloc()
		
