import appdaemon.plugins.hass.hassapi as hass
import globals

class KitchenLedController(hass.Hass):
  listen_event_handle_list = []
  def initialize(self):
    if not globals.check_args(self,['watch_entity', 'topic']):
      return

    self.listen_event_handle_list.append(self.listen_state(self.entity_changed, self.args['watch_entity']))

  def entity_changed(self, entity, attribute, old, new, kwargs):
    stete = "off"
    if new == "off":
      stete = "off"
    if new == "on":
      stete = "on"
    self.call_service("mqtt/publish", topic = self.args['topic'], payload = stete)
