import appdaemon.plugins.hass.hassapi as hass
import globals
import datetime
#
# Very special case, this will run sound 'alarm' on xiaomi gateway based on alarm clock event (alarmclock_trigger)
# and stop it when sensor became active.
# Args:
#
# sensor = sensor, which will stop alarm (bath motion sensor for me)
# ringtone = (default = 20) xiaomi ringtone id.
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AlarmclockAction(hass.Hass):
  timer = None
  ringtone = 20
  volume = 10
  gw_mac = ''
  def initialize(self):
    if not globals.check_args(self, ["sensor","gw_mac"]):
      return
    self.gw_mac = self.args['gw_mac']
    if 'ringtone' in self.args:
      self.ringtone = self.args['ringtone']
    self.listen_event(self.alarmclock_alarm, "alarmclock_alarm")
    self.listen_event(self.alarmclock_stop, "alarmclock_stop")
    self.listen_state(self.sensor_trigger, self.args['sensor'])

  def alarmclock_stop(self, event_id, event_args, kwargs):
    self.sensor_trigger(None, None, None, 'on', None)

  def sensor_trigger(self, entity, attribute, old, new, kwargs):
    if new == "on" and self.timer != None:
      self.call_service("xiaomi_aqara/stop_ringtone", gw_mac=self.gw_mac)
      self.cancel_current_timer()

  def alarmclock_alarm(self, event_id, event_args, kwargs):
    self.log('Alarm triggered!')
    self.volume = 10
    self.timer = self.run_every(self.timer_tick, self.datetime()+datetime.timedelta(seconds=15), 17)

  def timer_tick(self, kwargs):
    self.call_service("xiaomi_aqara/play_ringtone", gw_mac=self.gw_mac, ringtone_id=self.ringtone, ringtone_vol=self.volume)
    if self.volume < 100:
      self.volume = self.volume + 10

  def cancel_current_timer(self):
    if self.timer != None:
      self.log('canceling timer')
      self.cancel_timer(self.timer)
    self.timer = None
