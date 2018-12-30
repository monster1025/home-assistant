import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals

#
# App to send notifications when counters state needs attention
#
# Args:
#
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class WaterCountersAlarm(hass.Hass):
  checkup_threasold = 31
  send_threasold = 31

  def initialize(self):
    if not globals.check_args(self, ['checkup_threasold', 'send_threasold']):
      return
    self.checkup_threasold = self.args['checkup_threasold']
    self.send_threasold = self.args['send_threasold']
    
    self.check_send_dates({"force": 1})
    time = datetime.time(10, 0, 0)
    self.run_daily(self.check_checkup_dates, time)
    self.run_daily(self.check_send_dates, time)

  def check_send_dates(self, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return
    devices = self.get_state()
    values = {}
    send_devices = []
    for device in devices:
      send_date = None
      if "attributes" in devices[device]:
          if "date" in devices[device]["attributes"]:
            send_date = devices[device]["attributes"]["date"]
          if send_date != None:
            self.log('found device {} with send date {}'.format(device, send_date))
            if send_date == "":
                send_devices.append(device)
            else:
              send_date_date = None
              if '-' in send_date:
                send_date_date = datetime.datetime.strptime(send_date, '%Y-%m-%d')
              else:
                send_date_date = datetime.datetime.strptime(send_date, '%d.%m.%Y')
              if send_date_date < (datetime.datetime.now() - datetime.timedelta(days=self.send_threasold)):
                send_devices.append(device)
            values[device] = send_date

    message=""
    if send_devices:
      message += "ВНИМАНИЕ! У вас есть счетчики, показания по которым давно не передавались:\n"
      for device in send_devices:
        message += "- {}: {}\n".format(self.friendly_name(device), values[device])
      message += "\n\n"

    if send_devices or ("always_send" in self.args and self.args["always_send"] == 1) or ("force" in kwargs and kwargs["force"] == 1):
      if message != "":
        self.notify(message, name = "telegram")
    
  def check_checkup_dates(self, kwargs):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
      return

    devices = self.get_state()
    values = {}
    checkup_devices = []
    for device in devices:
      checkup = None
      if "attributes" in devices[device]:
          if "checkup" in devices[device]["attributes"]:
            checkup = devices[device]["attributes"]["checkup"]
          if checkup != None:
            self.log('found device {} with checkup date {}'.format(device, checkup))
            checkup_date = datetime.datetime.strptime(checkup, '%Y-%m-%d')
            if (checkup_date - datetime.timedelta(days=self.checkup_threasold)) < datetime.datetime.now():
              checkup_devices.append(device)
            values[device] = checkup

    message=""
    if checkup_devices:
      message += "ВНИМАНИЕ! У вас есть счетчик, нуждающийся в поверке:\n"
      for device in checkup_devices:
        message += "- {}: {}\n".format(self.friendly_name(device), values[device])
      message += "\n\n"

    if checkup_devices or ("always_send" in self.args and self.args["always_send"] == 1) or ("force" in kwargs and kwargs["force"] == 1):
      if message != "":
        self.notify(message, name = "telegram")