import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta
import datetime
import globals

#
# App to monitor high power usage when away.
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

class PowerWatchdog(hass.Hass):
  listen_event_handle_list = []
  notified_today = False
  standby_power_limit = 10

  def initialize(self):
    if not globals.check_args(self, ['entity', 'thresold', 'ha_panel', 'water_devices']):
      return
    self.listen_event_handle_list.append(self.listen_state(self.power_changed, self.args['entity']))

  def power_changed(self, entity, attribute, old, new, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return

    ha_panel_state = self.get_state(self.args['ha_panel'])
    if (ha_panel_state != "armed_away"):
     return
    # self.log('Power usage changed - {}kWh.'.format(new))

    # if water devices is on - then skipping this alert
    devices = self.args['water_devices']
    for device in devices:
      state = self.get_state(device)
      attributes = self.get_state(device, attribute = "all")['attributes']
      if 'load_power' not in attributes:
        continue
      load_power = attributes['load_power']
      # self.log('{} load power is: {}'.format(device, load_power))
      if state == 'on' and load_power > self.standby_power_limit:
        return

    power = float(new)
    if power > self.args['thresold']:
      if not self.notified_today:
        self.notified_today = True
        self.log('Power usage too much when away - {}kWh.'.format(new))
        self.notify('В ваше отсутствие наблюдается высокое потребление электроэнергии ({}), не оставили ли вы работающие устройства?'.format(power), name = 'telegram')
