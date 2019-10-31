import appdaemon.plugins.hass.hassapi as hass
import globals
#
# Управление замком Xiaomi
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class CurtainSecurity(hass.Hass):
  listen_event_handle_list = []
  def initialize(self):
    if not globals.check_args(self, ['curtain', 'door']):
      return
    self.listen_event_handle_list.append(self.listen_event(self.curtain_changed, event='call_service', entity_id = self.args['curtain']))

  def terminate(self):
    if self.listen_event_handle_list != None:
      for listen_event_handle in self.listen_event_handle_list:
        self.cancel_listen_event(listen_event_handle)

  def curtain_changed(self, event_name, data, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    service = data['service']
    if service in ['close_cover', 'open_cover']:
      door_state = self.get_state(self.args['door'])
      if door_state == "on":
        self.call_service("cover/stop_cover", entity_id = self.args['curtain'])