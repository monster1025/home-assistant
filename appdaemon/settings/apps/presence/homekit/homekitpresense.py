import appdaemon.plugins.hass.hassapi as hass

#
# Listen for homekit presence 
#
# Args:
# sensor - home presence 'sensor'
# ha_panel - alarm control panel entity (to arm and disarm).
# constraint - (optional, input_boolen), if turned off - alarm panel will be not armed\disarmed.
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class HomekitPresense(hass.Hass):
  def initialize(self):
    if "sensor" not in self.args or "arrive_event" not in self.args or "leave_event" not in self.args:
      self.error("Please provide sensor, arrive_event, leave_event in config!")
      return
    self.listen_state(self.sensor_trigger, self.args['sensor'])
  
  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if new == "on" and old == "off":
        self.fire_event(self.args['arrive_event'])
    elif new == "off" and old == "on":
        self.fire_event(self.args['leave_event'])
    self.log("{} turned {}".format(entity, new))
    self.notify("{} turned {}".format(entity, new), name = self.args['notify'])