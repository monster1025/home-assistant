import appdaemon.plugins.hass.hassapi as hass

class Noolite(hass.Hass):
  brightness = 25
  force = False

  def initialize(self):
    self.run_at_sunrise(self.sunrise_cb)
    self.run_at_sunset(self.sunset_cb)
    self.listen_state(self.light_change, "group.mainroom_light")
    self.listen_event(self.away_mode, "away_mode")

  def away_mode(self, event_id, event_args, kwargs):
    self.noolite_off()

  def light_change(self, entity, attribute, old, new, kwargs):
    sun_down = self.sun_down()
    if new == "off" and (sun_down or self.force):
      self.noolite_on(self.brightness)
    else:
      self.noolite_off()

  def noolite_off(self):
    self.log("Turning off salt lamp.")
    self.turn_off(self.args['entity_id'])

  def noolite_on(self, brightness=120):
    self.log("Turning on salt lamp for brightness {}.".format(brightness))
    self.turn_on(self.args['entity_id'], brightness=self.brightness)

  def sunset_cb(self, kwargs):
    self.noolite_on(self.brightness)

  def sunrise_cb(self, kwargs):
    self.noolite_off()
