import appdaemon.plugins.hass.hassapi as hass
import os

#
# App to send notification when doorbell is ringing
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

class Doorbell(hass.Hass):
  ringtone = 10
  gw_mac = ''
  def initialize(self):
    if "notify" not in self.args or "sensor" not in self.args or "camera" not in self.args:
      self.error("Please provide notify, sensor, camera in config!")
      return
    if "gw_mac" in self.args:
      self.gw_mac = self.args['gw_mac']

    if 'ringtone' in self.args:
      self.ringtone = self.args['ringtone']

    self.listen_state(self.sensor_trigger, self.args['sensor'])

  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if new != "off":
      return
    self.log("doorbell call")
    self.call_service("xiaomi_aqara/play_ringtone", gw_mac=self.gw_mac, ringtone_id=self.ringtone, ringtone_vol=100)
    self.notify("Звонок в дверь!!!", name = self.args['notify'])
    result = self.send_video()

  def send_video(self):    
    file = '/config/www/doorbell_video.mp4'
    if os.path.exists(file):
      os.remove(file)
    
    self.call_service("stream/record", stream_source=self.args['rtsp'], filename=file, duration=10)
    self.timer = self.run_in(self.run_in_send_video, 20, file=file)

  def run_in_send_video(self, args):
    extra_data = {'video': {'file': args['file'], 'caption': 'Видео звонившего.'}}
    self.notify("Видео звонившего", name = self.args['notify'], data=extra_data)


  def send_image(self):
    self.call_service("camera/snapshot", entity_id=self.args['camera'], filename="/config/www/camera_image.jpg")
    extra_data = {'photo': {'file':'/config/www/camera_image.jpg', 'capture': 'Фото звонившего.'}}
    self.notify("Фото звонившего", name = self.args['notify'], data=extra_data)
