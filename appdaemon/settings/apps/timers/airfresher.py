import appdaemon.plugins.hass.hassapi as hass
import globals
import datetime
#
# Entity timer
# Turn on and off this entities
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AirFresher(hass.Hass):
  timers = []
  fresh_times = 0

  def initialize(self):
    self.listen_state(self.light_change, 'group.bath_light')
    
  def light_change(self, entity, attribute, old, new, kwargs):
    if (old == "on" and new == "off"):
      self.log('Stop freshing timer.')
      self.cancel_timers()

    if (old == "off" and new == "on"):
      self.log('Start freshing timer.')
      self.fresh_times = 0
      newtime = self.datetime()+datetime.timedelta(minutes=3)
      self.timers.append(self.run_every(self.timer_tick, newtime, 5*60))

  def timer_tick(self, args) -> None:
    self.fresh()

  def cancel_timers(self) -> None:
    for timer in self.timers:
      self.cancel_timer(timer)
    timers = []

  def fresh(self):
    self.fresh_times = self.fresh_times + 1
    if (self.fresh_times > 5):
      self.log('Fresh max times is reached. Canceling timer.')
      self.cancel_timers()
      return
    self.log('freshing in {}'.format(self.fresh_times))
    self.call_service("mqtt/publish", topic = "home/airfresher/airfresher/fresh/set", payload = "1")
