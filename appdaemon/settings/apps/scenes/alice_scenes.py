import appdaemon.plugins.hass.hassapi as hass
import globals
#
# Управление сценариями из алисы
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AliceScenes(hass.Hass):
  listen_event_handle_list = []

  def initialize(self):
    if not globals.check_args(self, ['alice_prefix']):
      return
    devices = self.get_state()
    for device in devices:
      if not device.startswith(self.args['alice_prefix']):
        continue
      self.log("Listening for changes: {}".format(device))
      self.listen_event_handle_list.append(self.listen_state(self.alice_scene_trigger, device))

  def alice_scene_trigger(self, entity, attribute, old, new, kwargs):
    if new != 'on':
      return
    self.turn_off(entity)

    entity_name = entity.replace(self.args['alice_prefix'], "")
    self.log('Alice triggered scene: {}'.format(entity_name))
    if (entity_name == "turn_off_light"):
      self.turn_off_light()
    if (entity_name == "night_mode"):
      self.night_mode()
    if (entity_name == "away_mode"):
      self.away_mode()
    # if (entity_name == "turn_on_coffeemachine"):
    #   self.turn_on_coffeemachine()
    # if (entity_name == "make_coffee"):
    #   self.make_coffee()

  def terminate(self):
    if self.listen_event_handle_list != None:
      for listen_event_handle in self.listen_event_handle_list:
        self.cancel_listen_event(listen_event_handle)

  def turn_off_light(self):
    self.turn_off('group.mainroom_light')

  def night_mode(self):
    self.turn_off('switch.plug_158d0001104a0c') #tv
    self.turn_off('group.all_lights')
    self.call_service("cover/close_cover", entity_id = 'cover.curtain_158d0002b0c46a')

  def away_mode(self):
  	self.call_service("alarm_control_panel/alarm_arm_away", entity_id = self.args['ha_panel'])

  def turn_on_coffeemachine(self):
    self.log('Turn on coffeemachine')
    self.call_service("mqtt/publish", topic = 'home/coffee/coffee/power/set', payload = 'on')

  def make_coffee(self):
    self.log('Make coffee')
    self.call_service("mqtt/publish", topic = 'home/coffee/coffee/power/set', payload = 'on')
    self.timer = self.run_in(self.run_in_make_coffee, 30)
    self.log('Waiting for power on.')

  def run_in_make_coffee(self, args):
    self.call_service("mqtt/publish", topic = 'home/coffee/coffee/coffee/set', payload = 'on')
