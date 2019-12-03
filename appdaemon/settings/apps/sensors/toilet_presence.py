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
  timers = []
  presence_timeout = 30

  def initialize(self):
    if 'sensor' not in self.args:
      self.error("Please provide sensor in config!")
      return
    self.set_value("off", 0)
    self.listen_state(self.distance_changed, self.args['sensor'])
    
  def distance_changed(self, entity, attribute, old, new, kwargs):
    if new == 'unknown':
      return
    
    distance = float(new)
    state = ""
    if (distance > 1.100 or distance < 0.750):
      self.timers_off()
      self.timers.append(self.run_in(self.run_in_presense_off, self.presence_timeout))
      self.log('re-setting timer for {}s.'.format(self.presence_timeout))
      if (self.state != "on"):
        self.set_value("on", distance)
      

  def run_in_presense_off(self, args):
    self.set_value("off", 0)

  def timers_off(self):
    for timer in self.timers:
      self.cancel_timer(timer)

  def set_value(self, state, distance):
    self.log('Toilet presense: {}'.format(state))
    self.state = state
    entity_id = "sensor.toilet_presence"

    attributes = {}
    attributes['distance'] = distance
    attributes['description'] = 'Created and updated from appdaemon ({})'.format(__name__)

    self.set_state(entity_id, state = state, attributes = attributes)