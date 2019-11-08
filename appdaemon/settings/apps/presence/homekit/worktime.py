import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Listen for homekit presence 
#
# Args:
# arrive_event - Arrive event name.
# leave_event - Leave event name
# notify - notify platform
# constraint - (optional, input_boolen), if turned off - no notifications will be sent.
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class WorkTime(hass.Hass):
  arrive_time = None
  leave_time = None
  notify_time = None
  app_namespace = "worktime_namespace"
  work_hours = 9
  notify_before_leave_in_minutes = 15
  notify_every_seconds = 300
  timers = []

  def initialize(self):
    if 'notify' not in self.args or "arrive_event" not in self.args or "leave_event" not in self.args:
      self.error("Please provide arrive_event, leave_event in config!")
      return
    self.listen_event(self.arrive_event, self.args['arrive_event'])
    self.listen_event(self.leave_event, self.args['leave_event'])
    self.run_daily(self.reset_timer_tick, self.parse_time("23:59:59"))
    self.load_state()
    self.run_timer()

  def arrive_event(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    if self.arrive_time != None:
      self.log('You have already arrived to the work today at {}'.format(self.arrive_time))
      self.run_timer()
      return

    self.arrive_time = self.datetime()
    self.leave_time = self.datetime()+datetime.timedelta(hours=self.work_hours)
    self.notify_time = self.leave_time-datetime.timedelta(minutes=self.notify_before_leave_in_minutes)
    self.save_state()
    self.run_timer()
    self.log("Monster has arrived to work at {}, work till {}, will notify at {}.".format(self.arrive_time, self.leave_time, self.notify_time))
    self.timers.append(self.run_every(self.timer_tick, self.notify_time, self.notify_every_seconds))
    self.notify("Добро пожаловать в офис. Сегодня работаешь до {}.".format(self.format_time(self.leave_time)), name = self.args['notify'])

  def run_timer(self):
    if self.arrive_time == None:
      return
    timer_start = self.notify_time
    if timer_start<self.datetime():
      timer_start=self.datetime()+datetime.timedelta(seconds=self.notify_every_seconds)
    self.timers.append(self.run_every(self.timer_tick, timer_start, self.notify_every_seconds))

  def leave_event(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    if self.arrive_time == None:
      return
    self.cancel_timers()
    travelTime = ""
    if "work_to_home_time" in self.args:
      time_entity = self.get_state(self.args['work_to_home_time'], attribute='all')
      travel_time = time_entity['state']
      jams_rate = time_entity['attributes'].get('jamsrate', 0)
      travelTime = " Время в пути до дома: {} мин, пробки: {} баллов.".format(travel_time, jams_rate)

    if self.datetime()<self.notify_time:
      self.log("Monster leave work too early: {}<{}".format(self.datetime(), self.notify_time))
      message = "Ты рано ушел с работы (работаешь с {} до {}).{}".format(self.format_time(self.arrive_time), self.format_time(self.leave_time), travelTime)
    else:
      self.log("Monster leave work at {} - {}".format(self.arrive_time, self.datetime))
      message = "Рабочий день окончен ({}-{}). Приятной дороги домой.{}".format(self.format_time(self.arrive_time), self.format_time(self.datetime()), travelTime)
    self.notify(message, name = self.args['notify'])
    # self.reset_timer_tick(None)
    
  def timer_tick(self, args) -> None:
    self.log('timer tick')
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    if self.datetime()<self.notify_time:
      return
    message = "Ты пришел на работу в {}, работаешь до {}. Пора домой!".format(self.format_time(self.arrive_time), self.format_time(self.leave_time))
    self.notify(message, name = self.args['notify'])

  def cancel_timers(self) -> None:
    for timer in self.timers:
      self.cancel_timer(timer)
    self.timers = []

  def reset_timer_tick(self, kwargs):
    self.log("Resetting timer.")
    self.arrive_time = None
    self.leave_time = None
    self.notify_time = None
    self.save_state()

  def load_state(self):
    self.arrive_time=self.deserialize_datetime(self.get_state("sensor.arrive_time", namespace=self.app_namespace))
    self.leave_time=self.deserialize_datetime(self.get_state("sensor.leave_time", namespace=self.app_namespace))
    self.notify_time=self.deserialize_datetime(self.get_state("sensor.notify_time", namespace=self.app_namespace))
    self.log("App is reloaded. Saved values - arrive_time: {}, leave_time: {}, notify_time: {}".format(self.arrive_time, self.leave_time, self.notify_time))

  def save_state(self):
    self.set_state("sensor.arrive_time", state=self.serialize_datetime(self.arrive_time), namespace=self.app_namespace)
    self.set_state("sensor.leave_time", state=self.serialize_datetime(self.leave_time), namespace=self.app_namespace)
    self.set_state("sensor.notify_time", state=self.serialize_datetime(self.notify_time), namespace=self.app_namespace)
  
  def format_time(self, date):
  	return date.strftime("%H:%M")

  def serialize_datetime(self, date):
    if date is None:
      return None
    return date.isoformat()

  def deserialize_datetime(seld, date):
    if (date is None):
      return None
    return datetime.datetime.fromisoformat(date)
