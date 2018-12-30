import appdaemon.plugins.hass.hassapi as hass

#
# Pre alarm event.
# This app will slowly turn on the light after 'alarmclock_alarm' event. It will fire 15 mins(by default) before alarm.
# and stop when sensor became active.
#
# Args:
# sensor = sensor, which will stop pre-alarm (bath motion sensor for me)
# entity = entity to slowly turn on. Must support brightness control.
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AlarmclockPrealarm(hass.Hass):
  brightness = 1
  color_temp = 588
  timer = None
  def initialize(self):
    if "sensor" not in self.args or "entity" not in self.args:
      self.error("Please provide sensor and entity in config!")
      return
    self.listen_event(self.alarmclock_prealarm, "alarmclock_prealarm")
    self.listen_event(self.alarmclock_stop, "alarmclock_stop")
    self.listen_state(self.sensor_trigger, self.args['sensor'])

  def alarmclock_stop(self, event_id, event_args, kwargs):
    self.sensor_trigger(None, None, None, 'on', None)

  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if new == "on":
      if self.timer != None:
        self.brightness = 255
        self.color_temp = 240
        self.timer_tick(None)
      self.cancel_current_timer()

  def cancel_current_timer(self):
    if self.timer != None:
      self.log('canceling timer')
      self.cancel_timer(self.timer)
    self.timer = None

  def alarmclock_prealarm(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    self.log('Prealarm triggered!')
    self.brightness = 1
    self.color_temp = 588
    self.timer = self.run_every(self.timer_tick, self.datetime(), 10)

  def timer_tick(self, kwargs):
    attributes = self.get_state(self.args['entity'], attribute = "all")
    if 'attributes' in attributes:
      attributes = attributes['attributes']
    # we have a group here
    if 'entity_id' in attributes:
      for entity_id in attributes['entity_id']:
        self.make_entity_action(entity_id, None)
    else:
      # simple entity
      self.make_entity_action(self.args['entity'], attributes)

    if (self.brightness < 245):
      self.brightness = self.brightness + 2
    elif (self.color_temp > 220):
      self.color_temp = self.color_temp - 30
    else:
      self.cancel_current_timer()
    self.log("brightness: {}, color_temp: {}".format(self.brightness, self.color_temp))

  def make_entity_action(self, entity_id, attributes):
    if attributes == None:
      attributes = self.get_state(entity_id, attribute = "all")
    if 'attributes' in attributes:
      attributes = attributes['attributes']
    #state = self.get_state(entity_id)
    self.turn_on(entity_id, brightness = self.brightness, color_temp = self.color_temp)
    # self.log(attributes)
