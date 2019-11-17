import appdaemon.plugins.hass.hassapi as hass

#
# Helper for presence detection
#
# Args:
# ha_panel - alarm control panel entity (to arm and disarm).
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Presence(hass.Hass):
  def initialize(self):
  	self.log('started')

  def function():
  	pass