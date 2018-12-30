import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, date, timedelta

#
# Basic alarm clock.
# It will trigger 'alarmclock_trigger' event on alarm time.
#
# Args:
#
# time = input_datetime for time (alarm time).
# state = input_boolean for alarm state (on/off)
# days = list of days when alarm is active
# prealarm_delta (optional, in minutes, default=15) = time befor main alarm, when 'alarmclock_prealarm' event will fire (you can trigger slow light on before main alarm sound).
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class AlarmClock(hass.Hass):
  alarmtimer = None
  prealarmtimer = None
  prealarm_delta = 15
  def initialize(self):
    if "days" not in self.args or "time" not in self.args or "state" not in self.args:
      self.error("Please provide days, time and state in config!")
      return
    if 'prealarm_delta' in self.args:
      self.prealarm_delta = self.args['prealarm_delta']
    self.log('Alarm will trigger in days: {}.'.format(self.args['days']))
    self.listen_state(self.alarm_time_changed, self.args['time'])
    self.listen_state(self.alarm_time_changed, self.args['state'])
    self.alarm_time_changed(None, None, None, None, None)
 
  def alarm_time_changed(self, entity, attribute, old, new, kwargs):
    #cacnel old timer
    self.cancel_current_timer()

    alarm_state = self.get_state(self.args['state'])
    if alarm_state == 'off':
      self.log('Turning off alarm.')
      return

    #set new timer
    time_string = self.get_state(self.args["time"])
    if time_string == "unknown":
      return
    alarm_time = self.parse_time(time_string)
    self.run_timer(alarm_time)

  def run_timer(self, alarm_time):
    prealarm_time = (datetime.combine(date.min, alarm_time) - timedelta(0, self.prealarm_delta * 60)).time()
    self.alarmtimer = self.run_daily(self.alarmclock_trigger, alarm_time)
    self.prealarmtimer = self.run_daily(self.alarmclock_prealarm, prealarm_time)
    self.log("Alarm was set to {}, prealarm: {}.".format(alarm_time, prealarm_time))
 
  def cancel_current_timer(self):
    if self.alarmtimer != None and self.prealarmtimer != None:
      self.cancel_timer(self.alarmtimer)
      self.cancel_timer(self.prealarmtimer)
    
  def alarmclock_trigger(self, kwargs):
    if not self.constrain_days(self.args['days']):
      return
    self.log("Alarmclock triggered!")
    self.fire_event("alarmclock_alarm")

  def alarmclock_prealarm(self, kwargs):
    if not self.constrain_days(self.args['days']):
      return
    self.log("Pre alarmclock triggered!")
    self.fire_event("alarmclock_prealarm")
