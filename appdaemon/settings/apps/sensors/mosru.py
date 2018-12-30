import globals
import datetime as dt
from automation import Automation, Base
from datetime import datetime, tzinfo, timedelta
from mos_lib import MosAPI, Watercounter, Water, EmpServerException

class WaterCounterSender(Automation):
  timezone = '+03:00'
  def initialize(self):
    super().initialize()
    self.run_daily(self.send_mosru_counters, dt.time(12, 00, 0))
  
  def send_mosru_counters(self, kwargs):
    self.log('Starting sending counters value to mos.ru')
    new_values = []
    self.app.update_watercounters()
    water_hot = self.app.water_hot
    water_cold = self.app.water_cold
    counters = [water_hot, water_cold]

    for counter in counters:
        counter_type = counter['type']

        checkup = counter['checkup'].replace(self.timezone,'')
        checkup_date = datetime.strptime(checkup, '%Y-%m-%d')

        # подходит дата поверки
        if checkup_date < datetime.now():
            self.error('Counter {} checkup date is expired at {}!'.format(counter['counterId'], checkup))
            continue

        our_sensor = ""
        if counter_type == 1:
            our_sensor = self.entity_ids['cold']
        elif counter_type == 2:
            our_sensor = self.entity_ids['hot']
        real_value = int(float(self.get_state(our_sensor)))
        self.log("Updating counter {} ({}) to real value: {}".format(counter['counterId'], our_sensor, real_value))
        new_values.append(Watercounter.serialize_for_send(counter, real_value))

    if new_values:
        try:
          self.app.send_watercounters(new_values)
          self.log('Counters values was sent to mos.ru')
        except EmpServerException as err:
          self.log('error sending: {}'.format(err))


class WaterCounterSensor(Automation):
  timezone = '+03:00'
  def initialize(self):
    super().initialize()
    self.timer = self.run_every(self.update_sensors, self.datetime(), 1*60*60)

  def update_sensors(self, args) -> None:
    self.log('Updating water counters')
    self.app.update_watercounters()
    if 'hot' in self.entity_ids:
        water_hot = self.app.water_hot
        self.create_water_entity(self.entity_ids['hot'], water_hot)
    if 'cold' in self.entity_ids:
        water_cold = self.app.water_cold
        self.create_water_entity(self.entity_ids['cold'], water_cold)

  def create_water_entity(self, entity_id, counter):
    indication_max = 0
    indication_date = ""
    for indication in counter['indications']:
        current = float(indication['indication'])
        if (current > indication_max):
            indication_max = current
            indication_date = indication['period']
    indication_date = indication_date.replace(self.timezone,'')

    counter_type = counter['type']
    checkup = counter['checkup']
    type_desc = ""
    type_desc_ru = ""
    if counter_type == 1:
        type_desc = "cold"
        type_desc_ru = "Холодная"
    elif counter_type == 2:
        type_desc = "hot"
        type_desc_ru = "Горячая"

    icon = "mdi:av-timer"
    checkup = checkup.replace(self.timezone,'')
    checkup_date = datetime.strptime(checkup, '%Y-%m-%d')

    # подходит дата поверки
    if (checkup_date - timedelta(days=31)) < datetime.now():
        icon = "mdi:alert-octagon"

    attributes = {}
    attributes['unit_of_measurement'] = 'm3'
    attributes['date'] = indication_date
    attributes['checkup'] = checkup
    attributes['icon'] = icon
    attributes['friendly_name'] = "{}(mos.ru)".format(type_desc_ru)
    attributes['description'] = 'Created and updated from appdaemon ({})'.format(__name__)

    self.set_state(entity_id, state = indication_max, attributes = attributes)

class EpdBalanceSensor(Automation):
  def initialize(self):
    super().initialize()
    self.timer = self.run_every(self.update_sensors, self.datetime(), 1*60*60)

  def update_sensors(self, args) -> None:
    if 'epd_balance' in self.entity_ids:
        self.app.update_epd()
        epd_balance = self.app.epd_balance
        epd_description = self.app.epd_description
        self.log('Current epd balance: {}'.format(epd_balance))

        entity_id = self.entity_ids['epd_balance']
        attributes = {
            'unit_of_measurement': '₽',
            'icon': 'mdi:bank-transfer',
            'date': datetime.now().strftime('%d.%m.%Y'),
            'unpaid': epd_description,
            'friendly_name': 'Баланс (ЕПД)',
            'description': 'Created and updated from appdaemon ({})'.format(__name__)
        }
        self.set_state(entity_id, state = epd_balance, attributes = attributes)


class MosruBase(Base):
  _api = None
  _flat_id = None
  _guid='4421a3fb0567714b27dec84d3c3862dc'
  _app_version = '3.5.0.195 (102)'
  _user_agent = 'okhttp/3.8.1'
  _dev_user_agent = 'Android'
  _timezone = '+03:00'

  def initialize(self):
    super().initialize()
    if not globals.check_properties(self,['login', 'pwd', 'token', 'paycode']):
      return
    self._api = MosAPI(token=self.properties['token'],
                 user_agent=self._user_agent,
                 guid=self._guid,
                 dev_user_agent=self._dev_user_agent,
                 dev_app_version=self._app_version,
                 timeout=6)
    self._set_flat_id()

  def _set_flat_id(self):
    ''' Set flat id by properties or pay code '''
    if 'flat_id' in self.properties:
        self._flat_id = self.properties['flat_id']
        return
    if (self._flat_id != None):
        return
    self._check_login()
    flats = self._api.get_flats()
    for flat in flats:
        if (int(flat['paycode']) != self.properties['paycode']):
            continue
        self._flat_id = flat['flat_id']

  def _check_login(self):
    if not self._api.is_active():
        self._api.login(self.properties['login'], self.properties['pwd'])

class MosruPower(MosruBase):
  _power_counters = None

  @property
  def power_total(self):
    if (self._power_counters == None):
        self.update_power()
    return self._power_counters['zones'][0]['value']

  @property
  def power_balance(self):
    if (self._power_counters == None):
        self.update_power()
    return float(self._power_counters['balance'])

  def update_power(self) -> None:
    self._check_login()
    self._power_counters = self._api.get_electrocounters(self._flat_id)

class MosruWater(MosruBase):
  _water_counters = None

  @property
  def water_hot(self):
    """Return the current state of counter."""
    if (self._water_counters == None):
        self.update_watercounters()
    hots_json = list(filter(lambda x: x['type'] == Water.HOT, self._water_counters))
    return hots_json[0]

  @property
  def water_cold(self):
    """Return the current state of counter."""
    if (self._water_counters == None):
        self.update_watercounters()
    colds_json = list(filter(lambda x: x['type'] == Water.COLD, self._water_counters))
    return colds_json[0]

  @property
  def water_hot_value(self):
    hot_value = Watercounter.last_value(self.water_hot)
    return hot_value

  @property
  def water_cold_value(self):
    cold_value = Watercounter.last_value(self.water_cold)
    return cold_value


  def send_watercounters(self, new_values) -> None:
    self._check_login()
    self._api.send_watercounters(self._flat_id, new_values)

  def update_watercounters(self) -> None:
    self._check_login()
    self._water_counters = self._api.get_watercounters(self._flat_id)['counters']

class MosruEpd(MosruBase):
  _epd_data = None

  @property
  def epd_description(self) -> str:
    if (self._epd_data == None):
        self.update_epd()

    unpaid = []
    for date in self._epd_data:
      epd = self._epd_data[date]
      if epd['is_paid']:
        continue
      unpaid.append('{}: {}'.format(date, epd['amount']))
    return ", ".join(unpaid)


  @property
  def epd_balance(self) -> float:
    """Return the current state of counter."""
    if (self._epd_data == None):
        self.update_epd()
    balance = 0
    for date in self._epd_data:
      epd = self._epd_data[date]
      epd_is_paid = epd['is_paid']
      if epd_is_paid:
        continue
      balance = balance - epd['amount']
    return balance

  def update_epd(self) -> None:
    self._check_login()
    data = {}
    date = datetime.now().date()
    for i in range (0,6):
      process_date = date - timedelta(i*365/12)
      date_str = process_date.strftime('%d.%m.%Y')
      epd = self._api.get_epd(self._flat_id, date_str, False)
      for i in range(0, 10): #retries
        if epd != []:
          break
        epd = self._api.get_epd(self._flat_id, date_str, False)
      epd_first = epd[0]
      data[date_str] = epd_first
      # epd_total = epd_first['amount']
      # epd_is_paid = epd_first['is_paid']
      # self.log(" - Дата: {}, сумма: {}, оплачен: {}.".format(date_str, epd_total, epd_is_paid))
    self._epd_data = data

class MosruClient(MosruEpd, MosruWater, MosruPower):
  def initialize(self):
    super().initialize()
    # self.log('Flat id is: {}'.format(self._flat_id))
    # self.log('epd balance: {}'.format(self.epd_balance))
    # self.log('cold: {}'.format(self.water_cold))
    # self.log('hot: {}'.format(self.water_hot))
    # self.log('power_counter: {}, balance: {}'.format(self.power_total, self.power_balance))
