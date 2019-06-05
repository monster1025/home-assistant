import appdaemon.plugins.hass.hassapi as hass
import globals
#
# Entity timer
# Turn on and off this entities
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Curtain(hass.Hass):
  def initialize(self):
    if not globals.check_args(self, ["on_time", "off_time"]):
      return
    on_time = self.parse_time(self.args["on_time"])
    off_time = self.parse_time(self.args["off_time"])

    self.on_timer = self.run_daily(self.on_timer_tick, on_time)
    self.off_timer = self.run_daily(self.off_timer_tick, off_time)

  def on_timer_tick(self, kwargs):
    self.log('on_timer')
    if 'entity' in self.args:
      self.call_service("cover/open_cover", entity_id = self.args['entity'])

  def off_timer_tick(self, kwargs):
    self.log('off_timer')
    if 'entity' in self.args:
      self.call_service("cover/close_cover", entity_id = self.args['entity'])
      
