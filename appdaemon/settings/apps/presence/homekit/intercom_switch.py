import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Intercom auto open switch by presence
#
# Args:
# entity_id - intercom autp open switch
# arrive_event - Arrive event name.
# leave_event - Leave event name
# constraint - (optional, input_boolen), if turned off - no notifications will be sent.
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class IntercomSwitch(hass.Hass):
  def initialize(self):
    if "entity_id" not in self.args or "arrive_event" not in self.args or "leave_event" not in self.args:
      self.error("Please provide entity_id, arrive_event, leave_event in config!")
      return
    self.listen_event(self.arrive_event, self.args['arrive_event'])
    self.listen_event(self.leave_event, self.args['leave_event'])

  def arrive_event(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    entity_id = self.args['entity_id']
    self.log("Somebody come home, turn on {}".format(entity_id))
    self.turn_on(entity_id)
    self.notify("Кто-то вернулся домой, включаю домофон.", name = self.args['notify'])


  def leave_event(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    entity_id = self.args['entity_id']
    self.log("All persons leave home, turn off {}".format(entity_id))
    self.turn_off(entity_id)
    self.notify("Все ушли из дома, выключаю домофон", name = self.args['notify'])