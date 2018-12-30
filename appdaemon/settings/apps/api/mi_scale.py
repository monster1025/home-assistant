import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals

#
# App recieves xiaomi scale readings, parse user weight and set sensor in home-assistant
#
# Args:
#
# sensor = generated sensor name
# friendly_name (optional) = sensor friendly name
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class MiScale(hass.Hass):
  def initialize(self):
    if not globals.check_args(self, ["sensor"]):
      return
    self.register_endpoint(self.api_call)
    self.log('started')

  def api_call(self, data):
    # filter only my data
    prev_weight = 70
    weight_date = datetime.datetime.now()
    for current in data:
      if abs(current['Weight'] - prev_weight) > 5:
        continue
      # self.log(current)
      prev_weight = current['Weight']
      weight_date = current['Time']

    attributes = {}
    attributes['datetime'] = weight_date
    attributes['unit_of_measurement'] = 'kg'
    attributes['description'] = 'Created and updated from appdaemon (mi_scale)'
    if 'friendly_name' in self.args:
      attributes['friendly_name'] = self.args['friendly_name']

    self.set_state(self.args['sensor'], state = prev_weight, attributes = attributes)
    return 'ok', 200

