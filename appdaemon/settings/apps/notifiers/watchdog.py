import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta
import datetime
import globals

#
# App to monitor entity update time.
#
# Args:
#
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Watchdog(hass.Hass):
  listen_event_handle_list = []
  timezone = 3
  def initialize(self):
    if not globals.check_args(self, ['entity','update_interval', 'timeout']):
      return
    self.timer = self.run_every(self.watchdog_check, self.datetime(), self.args['update_interval'])

  def watchdog_check(self, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return

    entity = self.args['entity']
    attributes = self.get_state(entity, attribute='all')
    if not 'last_changed' in attributes:
      return
    last_changed = attributes['last_changed']
    last_changed_date = datetime.datetime.strptime(last_changed, '%Y-%m-%dT%H:%M:%S.%f+00:00') + timedelta(hours=self.timezone)
    time_diff = datetime.datetime.now() - last_changed_date
    if time_diff.seconds > self.args['timeout']:
      self.log('Entity {} was changed {} seconds ago.'.format(entity, time_diff.seconds))

      friendly_name = self.friendly_name(entity)
      message = "Датчик {} ({}) не обновлялся в течении {} секунд.".format(friendly_name, entity, self.args['timeout'])
      self.notify(message, name = "telegram")