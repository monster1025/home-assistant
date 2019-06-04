import appdaemon.plugins.hass.hassapi as hass

#
# Water leak detector
# close water valve and send a report
#
# Args:
#
# sensor = water leak sensor group
# valve = water valve - app will close it, when leak is detected
# notify = notify name to send notification
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class ToiletPresence(hass.Hass):
  state = ""

  def initialize(self):
    if 'sensor' not in self.args:
      self.error("Please provide sensor in config!")
      return
    self.listen_state(self.distance_changed, self.args['sensor'])
    
  def distance_changed(self, entity, attribute, old, new, kwargs):
    distance = int(new)

    if distance > 1000 or distance < 850:
      if self.state == "" or self.state == "off":
        self.set_value("on")
    elif distance < 1000 and distance > 850:
      if self.state == "" or self.state == "on":
        self.set_value("off")

  def set_value(self, state):
    self.log('Toilet presense: {}'.format(state))
    self.state = state
    entity_id = "sensor.toilet_presence"

    attributes = {}
    attributes['description'] = 'Created and updated from appdaemon ({})'.format(__name__)

    self.set_state(entity_id, state = state, attributes = attributes)