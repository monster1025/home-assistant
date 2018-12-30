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

class Lock(hass.Hass):
  def initialize(self):
    self.listen_event_handle_list = []
    if not globals.check_args(self, ['notify']):
      return
    locks = globals.get_group_entities(self, "group.all_locks")
    for lock in locks:
       self.listen_event_handle_list.append(self.listen_state(self.lock_state_changed, lock))

  def lock_state_changed(self, entity, attribute, old, new, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return

    state = new
    changed_by = self.get_state(entity, attribute = 'changed_by')
    verified_wrong_times = self.get_state(entity, attribute = 'verified_wrong_times')

    if verified_wrong_times > 0:
      message = "Попытка №{} отрыть замок с неправильным пальцем или паролем!".format(verified_wrong_times)
      self.notify(message, name = self.args['notify'])

    if state == "unlocked":
      user = changed_by
      user_var = "user_{}".format(changed_by)
      if user_var in self.args:
        user = self.args[user_var]
      message = "Открыта дверь пользователем: {}.".format(user)
      self.notify(message, name = self.args['notify'])
