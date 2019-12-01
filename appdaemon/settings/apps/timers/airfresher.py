import appdaemon.plugins.hass.hassapi as hass
import globals
import datetime
#
# Air Fresher controller
# Fresh the air in toilet
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
  fresh_times_max = 5
  fresh_every_mins = 1
  last_fresh_date = None

  def initialize(self):
    self.listen_state(self.light_change, 'group.bath_light')
    
  def light_change(self, entity, attribute, old, new, kwargs):
    if (old == "on" and new == "off"):
      self.log('Stop freshing timer.')
      self.cancel_timers()

    if (old == "off" and new == "on"):
      if self.last_fresh_date != None:
        diff = (self.datetime()-self.last_fresh_date).seconds / 60 # * 24 * 60 * 60
        if (diff < self.fresh_every_mins):
          self.log("time passed from last fresh: {}".format(diff))
          self.log('Already dreshed in {} mins.'.format(self.fresh_every_mins))
          return
      self.start_timer()

  def start_timer(self) -> None:
      self.log('Start freshing timer.')
      self.last_fresh_date = self.datetime()
      self.fresh_times = 0
      newtime = self.datetime()+datetime.timedelta(seconds=15)
      self.timers.append(self.run_every(self.timer_tick, newtime, self.fresh_every_mins*60))

  def cancel_timers(self) -> None:
    for timer in self.timers:
      self.cancel_timer(timer)
    timers = []

  def timer_tick(self, args) -> None:
    toilet_presence = self.get_state("sensor.toilet_presence")
    self.log('Timer ticked, presence is: {}'.format(toilet_presence))
    if (toilet_presence == "on"):
      self.fresh()

  def fresh(self):
    self.log("current timer: {}".format(self.last_fresh_date))

    self.fresh_times = self.fresh_times + 1
    if (self.fresh_times > self.fresh_times_max):
      self.log('Fresh max times is reached. Canceling timer.')
      self.cancel_timers()
      return

    self.log('freshing in {}'.format(self.fresh_times))
    self.turn_on(self.args['entity_id'])
    # self.call_service("mqtt/publish", topic = "home/airfresher/airfresher/fresh/set", payload = "1")
