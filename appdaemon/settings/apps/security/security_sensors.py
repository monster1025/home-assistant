import appdaemon.plugins.hass.hassapi as hass

#
# Security sensors alarm notification
# Send notification if some movement is detecter or door any is open
# while nobody is home
#
# Args:
# sensor - gorup of sensors to listen
# ha_panel - alarm panel entity
# notify - notify entity to send message
# 
# Release Notes
#
# Version 1.0:
#   Initial Version

class SecuritySensorsReport(hass.Hass):
  def initialize(self):
    if 'sensor' not in self.args or 'ha_panel' not in self.args or 'notify' not in self.args:
      self.error("Please provide sensor, ha_panel and notify in config!")
      return
    
    attributes = self.get_state(self.args['sensor'], attribute = "all")
    if 'attributes' in attributes:
      attributes = attributes['attributes']
    if 'entity_id' in attributes:
      for entity_id in attributes['entity_id']:
        self.listen_state(self.sensor_trigger, entity_id)

  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return

    if old != new and new == "on":
      alarm_panel_state = self.get_state(self.args['ha_panel'])
      if alarm_panel_state != "armed_away":
        return
      self.alarm_triggered(entity, old, new)

  def alarm_triggered(self, entity, old, new):
    self.log('alarm triggered')
    self.call_service("alarm_control_panel/alarm_trigger", entity_id = self.args['ha_panel'])

    friendly_name = self.friendly_name(entity)
    entity = entity.replace('_', '-')
    message = "В ваше отсутствие сработал датчик безопастности {} ({}) = {}->{}!".format(friendly_name, entity, old, new)
    self.notify(message, name = self.args['notify'])