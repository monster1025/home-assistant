#cube_tap_twice
import appdaemon.plugins.hass.hassapi as hass

#
# This app reacts to xiaomi cube events
#
# Args:
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Cube(hass.Hass):
  def initialize(self):
    self.listen_event(self.cube_flip90, "cube_flip90")
    self.listen_event(self.cube_flip180, "cube_flip180")
    self.listen_event(self.cube_shake_air, "cube_shake_air")
    self.listen_event(self.cube_move, "cube_move")
    self.listen_event(self.cube_tap_twice, "cube_tap_twice")
    self.listen_event(self.cube_swing, "cube_swing")
    
  def cube_flip90(self, event_id, event_args, kwargs):
    self.log("cube_flip90")
    # turn on next light
    self.fire_event("button_mainroom_click")

  def cube_flip180(self, event_id, event_args, kwargs):
    self.log("cube_flip180")

  def cube_shake_air(self, event_id, event_args, kwargs):
    self.log("cube_shake_air")

  def cube_move(self, event_id, event_args, kwargs):
    self.log("cube_move")

  def cube_swing(self, event_id, event_args, kwargs):
    self.log("cube_swing")

  def cube_tap_twice(self, event_id, event_args, kwargs):
    self.log("cube_tap_twice")
    attributes = self.get_state("group.mainroom_light", attribute = "all")
    if 'attributes' in attributes:
      attributes = attributes['attributes']
    self.log(attributes)
    for entity_id in attributes["entity_id"]:
      self.turn_off(entity_id)