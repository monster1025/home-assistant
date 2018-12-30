import appdaemon.plugins.hass.hassapi as hass

#
# Work leave reminder
# Send reminder about 'time to leave your work'
#
# Args:
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class WorkPresence(hass.Hass):
  def initialize(self):
    self.listen_event(self.office_enter, "office_enter")
    self.listen_event(self.office_leave, "office_leave")
    self.listen_event(self.office_leave_reminder, "office_leave_reminder")

  def office_leave_reminder(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    self.log('leave_reminder')
    enter_time = self.get_state('sensor.work_enter_time')
    leave_time = self.get_state('sensor.work_plan_leave_time')
    if 'payload' in event_args:
    	leave_time = event_args['payload']
    message = "Ты пришел на работу в {}, работаешь до {}. Пора домой!".format(enter_time, leave_time)
    self.call_service('notify/telegram', message=message)

  def office_leave(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    self.log('leave')
    work_to_home_time = self.get_state('sensor.work_to_home_time')
    message="Время в пути до дома {} минут.".format(work_to_home_time)
    self.call_service('notify/telegram', message=message)

  def office_enter(self, event_id, event_args, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    self.log('enter')
    enter_time = event_args.get('payload', None)
    if enter_time == '' or enter_time == None:
      return
    self.log(enter_time)
    self.call_service('notify/telegram', message='Добро пожаловать в офис. Приятного дня =)))')