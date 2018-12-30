import appdaemon.plugins.hass.hassapi as hass

#
# This app fix event turn off after hass restart
#
# Args:
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AutomationFix(hass.Hass):
  def initialize(self):
    self.listen_event(self.ha_event, "plugin_started")

  def ha_event(self, event_name, data, kwargs):
    self.run_in(self.turn_on_automations_timer, 10)

  def turn_on_automations_timer(self, kwargs):
    self.log('turning on automations')
    self.call_service('automation/turn_on', entity_id='group.all_automations')