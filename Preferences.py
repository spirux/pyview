# -*- coding: utf-8 -*-
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
			self = super(Preferences, self).initWithWindowNibName_owner_("PreferencesWindow", self)
			sharedInstance = self
		return sharedInstance
	
	def dealloc(self):
		if not self is sharedInstance:
			super(Preferences, self).dealloc()

		
def getPreference(prefname, defaultValue = None):
	"Read a user preference from the NSDefaults system."
	defaults = NSUserDefaults.standardUserDefaults()
	val = defaults.objectForKey_(prefname)
	if val is None:
		if defaultValue:
			return defaultValue
		else:
			raise KeyError(prefname)
	return val
		
def setPreference(prefname, value):
	defaults = NSUserDefaults.standardUserDefaults()
	defaults.setObject_forKey_(value, prefname)
	defaults.synchronize()
 
