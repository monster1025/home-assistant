import appdaemon.plugins.hass.hassapi as hass

#
# App to send notification when intercom is ringing
#
# Args:
#
# notify = notification platform to send notifications to
# ringtone (optional) = ringtone to play
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Intercom(hass.Hass):
  ringtone = 10
  gw_mac = ''
  def initialize(self):
    if 'chat_id' not in self.args or "notify" not in self.args:
      self.error("Please provide chat_id, notify in config!")
      return
    if "gw_mac" in self.args:
      self.gw_mac = self.args['gw_mac']

    if 'ringtone' in self.args:
      self.ringtone = self.args['ringtone']
    self.listen_event(self.domofon_call, "domofon_call")
    self.listen_event(self.receive_telegram_callback, 'telegram_callback')
    self.listen_state(self.sensor_trigger, self.args['sensor'])

  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if new != "off":
      return
    self.log("domofon_call")
    self.domofon_call(None, None, None)


  def domofon_call(self, event_id, event_args, kwargs):
    self.log("domofon_call")
    self.log(event_args)
    self.call_service("xiaomi_aqara/play_ringtone", gw_mac=self.gw_mac, ringtone_id=self.ringtone, ringtone_vol=100)
    keyboard = [[("Открыть", "/domofon_open")]]
    self.call_service('telegram_bot/send_message',
                      target=self.args['chat_id'],
                      message="Звонок в домофон!!!",
                      disable_notification=False,
                      inline_keyboard=keyboard)

  def receive_telegram_callback(self, event_id, payload_event, *args):
      """Event listener for Telegram callback queries."""
      assert event_id == 'telegram_callback'
      data_callback = payload_event['data']
      callback_id = payload_event['id']
      chat_id = payload_event['chat_id']

      if data_callback == '/domofon_open':
        self.turn_on("switch.domofon_open")
        self.turn_off("switch.domofon_open")
        self.call_service('telegram_bot/answer_callback_query',
                  message='Готово',
                  callback_query_id=callback_id)