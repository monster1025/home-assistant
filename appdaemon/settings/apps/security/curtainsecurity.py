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
  def initialize(self):
    if not globals.check_args(self, ['curtain', 'door']):
      return
    self.listen_event(self.curtain_changed, event='call_service', entity_id = self.args['curtain'])
    # self.listen_event_handle_list = []
    # locks = globals.get_group_entities(self, "group.all_locks")
    # for lock in locks:
    #    self.listen_event_handle_list.append(self.listen_state(self.lock_state_changed, lock))

  def curtain_changed(self, event_name, data, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    service = data['service']
    if service in ['close_cover', 'open_cover']:
      door_state = self.get_state(self.args['door'])
      if door_state == "on":
        self.call_service("cover/stop_cover", entity_id = self.args['curtain'])