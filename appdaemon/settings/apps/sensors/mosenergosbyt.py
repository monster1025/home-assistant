import requests
import hashlib
import globals
import datetime as dt
from xml.etree import ElementTree
from automation import Automation, Base  # type: ignore

class MosEnergoSbytSender(Automation):
  def initialize(self):
    super().initialize()
    self.run_daily(self.send_mosenergosbyt_counters, dt.time(12, 0, 0))
    # self.send_mosenergosbyt_counters({})

  def send_mosenergosbyt_counters(self, kwargs):
    if not 'home_power_total' in self.entity_ids:
        self.error('Please define home_power_total in entity_ids.')
        return

    current_counter_value = int(float(self.get_state(self.entity_ids['home_power_total'])))
    self.log('Sending current counter value: {}'.format(current_counter_value))
    self.app.send(current_counter_value)


class MosEnergoSbytUpdater(Automation):
  def initialize(self):
    super().initialize()
    self.timer = self.run_every(self.update_sensors, self.datetime()+timedelta(seconds=10), 1*60*60)
    # self.send_mosenergosbyt_counters({})

  def update_sensors(self, args) -> None:
    self.app.update()
    counter_value = self.app.value
    counter_date = self.app.date
    balance = self.app.balance
    self.log('Current counter value is: {} (@{}), balance is: {}'.format(counter_value, counter_date, balance))

    if 'mosenergosbyt_total' in self.entity_ids:
        entity_id = self.entity_ids['mosenergosbyt_total']
        attributes = {
            'unit_of_measurement': 'kWh',
            'date': counter_date,
            # 'checkup': checkup,
            'icon': 'mdi:av-timer',
            'friendly_name': 'Счетчик (мосэнергосбыт)',
            'description': 'Created and updated from appdaemon ({})'.format(__name__)
        }
        self.set_state(entity_id, state = counter_value, attributes = attributes)

    if 'mosenergosbyt_balance' in self.entity_ids:
        entity_id = self.entity_ids['mosenergosbyt_balance']
        attributes = {
            'unit_of_measurement': '₽',
            'date': counter_date,
            'icon': 'mdi:bank-transfer',
            'friendly_name': 'Баланс (мосэнергосбыт)',
            'description': 'Created and updated from appdaemon ({})'.format(__name__)
        }
        self.set_state(entity_id, state = balance, attributes = attributes)

class MosEnergoSbytCounter(Base):
  _version = 13
  _device = "android/11.2.6/2.9.15(105)"
  _session = None
  _profile = None
 
  # def initialize(self):
  #   super().initialize()

  @property
  def value(self) -> float:
    """Return the current state of counter."""
    if (self._profile == None):
        self.update()
    return float(self._profile['SH_POK_STR'])

  @property
  def balance(self) -> float:
    """Return the current state of counter."""
    if (self._profile == None):
        self.update()
    balance = -1 * float(self._profile['SM_DEBT'])
    if balance == -0:
        balance = 0
    return balance

  @property
  def date(self) -> str:
    """Return the current state of counter."""
    if (self._profile == None):
        self.update()
    return self._profile['DT_POK']
  
  def is_active(self):
    """
    :return: True если уже залогинился
    """
    return self._session is not None

  def update(self) -> None:
    if not self.is_active():
        self._session = self._get_session()
    url = 'https://lkkbyt.mosenergosbyt.ru/gate/do?api_version={}&id_session={}&process=refresh&type=1'.format(self._version, self._session)
    response = requests.get(url).text
    values_response = self._parse_response(response)
    self._profile = values_response
    # self.log(values_response)
  
  def send(self, value) -> bool:
    if not self.is_active():
        self._session = self._get_session()

    url = 'https://lkkbyt.mosenergosbyt.ru/gate/do?id_session={}&pr_check_ras=0&pr_flat_pu=0&process=dotranspok&type=3&vl_pok_t1={}&vl_pok_t2=0&vl_pok_t3=0'.format(self._session, value)
    response = requests.get(url).text
    send_response = self._parse_response(response)
    result = send_response['KD_RESULT']
    if result == 0:
        return True
    return False

  def _get_session(self) -> str:
    login = str(self.properties['login'])
    pass_md5 = hashlib.md5(self.properties['pwd'].encode('utf-8')).hexdigest()
    ls = ''
    phone = ''
    if len(login) == 10:
        ls = login
    elif len(login) == 11:
        phone = login
    else:
        self.error('unknown login type: {}'.format(login))
        return
    url = "https://lkkbyt.mosenergosbyt.ru/gate/do?api_version={}&id_device={}&phone={}&ls={}&process=login&pw_abn={}&type=1".format(self._version, self._device, phone, ls, pass_md5)
    response = requests.get(url).text
    session_response = self._parse_response(response)
    if ('ID_SESSION' not in session_response):
    	return
    session = session_response['ID_SESSION']
    return session

  def _parse_response(self, response):
    et = ElementTree.fromstring(response)

    headers = []
    values = []
    for node in et.findall('./h/p'):
        headers.append(node.text)
    for node in et.findall('./b/p'):
        values.append(node.text)

    result = {}
    if len(headers) == 0:
        return result

    for i in range(0, len(headers)):
        if i>=len(headers) or i>=len(values):
            continue
        header = headers[i]
        value = values[i]
        result[header] = value

    if 'NM_RESULT' in result and 'Вышла новая версия приложения' in result['NM_RESULT']:
        self.error('[!] new version is available. Please update: {}.'.format(result))

    return result
