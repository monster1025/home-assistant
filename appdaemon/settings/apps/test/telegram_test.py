import appdaemon.plugins.hass.hassapi as hass
import requests
import json

class TelegramTest(hass.Hass):
  def initialize(self):
      """Listen to Telegram Bot events of interest."""
      self.listen_event(self.receive_telegram_text, 'telegram_text')

  def receive_telegram_text(self, event_id, payload_event, *args):
      """Text repeater."""
      assert event_id == 'telegram_text'
      user_id = payload_event['user_id']
      msg = payload_event['text']
      self.log('got msg: {}'.format(msg))
      if msg.startswith('https://www.youtube.com/watch') or msg.startswith('https://youtube.com/watch'):
        self.sendToScreen(payload_event['text'])
  
  def sendToScreen(self, video_url):
      auth_data = {
              'login': self.args.get('alice_login', ''),
              'passwd': self.args.get('alice_pwd', '')
              }
      # self.log('auth_data: {}'.format(auth_data))

      s = requests.Session()
      s.get("https://passport.yandex.ru/")
      s.post("https://passport.yandex.ru/passport?mode=auth&retpath=https://yandex.ru", data=auth_data)
      
      Session_id = s.cookies["Session_id"]
      self.log('session: {}'.format(Session_id))
      
      # Getting x-csrf-token
      token = s.get('https://frontend.vh.yandex.ru/csrf_token').text
      self.log('token: {}'.format(token))

      # Detting devices info TODO: device selection here
      devices_online_stats = s.get("https://quasar.yandex.ru/devices_online_stats").text
      devices = json.loads(devices_online_stats)["items"]
      self.log('devices: {}'.format(devices))
      if not devices[0].get('screen_present', False):
        self.log('Device has no screen present.')
        return

      if "&feature=share" in video_url:
        video_url = video_url.replace("&feature=share", '')

      # Preparing request
      headers = {
          "x-csrf-token": token,
      }

      data = {
          "msg": {
              "provider_item_id": video_url
          },
          "device": devices[0]["id"]
      }

      if "https://www.youtube" in video_url:
          data["msg"]["player_id"] = "youtube"
          
      self.log('sending data: {}'.format(data))

      # Sending command with video to device
      res = s.post("https://yandex.ru/video/station", data=json.dumps(data), headers=headers)

      return res.text