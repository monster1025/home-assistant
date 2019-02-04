import appdaemon.plugins.hass.hassapi as hass
import globals

class KitchenLedController(hass.Hass):
  listen_event_handle_list = []
  def initialize(self):
    if not globals.check_args(self,['watch_entity']):
      return

    self.listen_event_handle_list.append(self.listen_state(self.entity_changed, self.args['watch_entity']))

  def entity_changed(self, entity, attribute, old, new, kwargs):
    if 'topic' in self.args:
      self.call_service("mqtt/publish", topic = self.args['topic'], payload = new)
    if 'control_entity' in self.args:
      if new == "on":
        self.turn_on(self.args['control_entity'])
      if new == "off":
        self.turn_off(self.args['control_entity'])