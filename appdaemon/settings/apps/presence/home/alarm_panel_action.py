import appdaemon.plugins.hass.hassapi as hass

#
# Listen for Alarm panel state change and fire an events ('away_mode' and 'return_home_mode')
#
# Args:
# ha_panel - alarm control panel entity.
# Release Notes
#
# Version 1.0:
#   Initial Version

class AlarmPanelAction(hass.Hass):
  def initialize(self):
    if "ha_panel" not in self.args:
      self.error("Please provide ha_panel in config!")
      return
    self.listen_state(self.ha_panel_trigger, self.args['ha_panel'])

  def ha_panel_trigger(self, entity, attribute, old, new, kwargs):
    # не срабатываем на triggered.
    if new == "armed_away" and old != "triggered":
      self.away_mode()
    if new == "disarmed" and old == "armed_away":
      self.return_home_mode()
  
  def away_mode(self):
    self.log('away_mode')
    self.fire_event('away_mode')

  def return_home_mode(self):
    self.log('return_home_mode')
    self.fire_event('return_home_mode')