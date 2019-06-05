import appdaemon.plugins.hass.hassapi as hass
import struct
import binascii

class Climate(hass.Hass):
  ir_topic = "home/remote/rm2/code/set"
  split_state = "None"
  timer = None

  def initialize(self):
    self.listen_event_handle_list = []
    if "ha_panel" not in self.args or "door_window" not in self.args:
      self.error("Please provide temp_sensor, ha_panel, door_window in config!")
      return
    self.listen_event_handle_list.append(self.listen_state(self.constraint_changed, self.args['constraint']))
    self.listen_event_handle_list.append(self.listen_state(self.ha_panel_changed, self.args['ha_panel']))
    self.listen_event_handle_list.append(self.listen_state(self.door_window_changed, self.args['door_window']))

    self.listen_event_handle_list.append(self.listen_state(self.nest_changed, 'binary_sensor.nest_y1'))
    self.listen_event_handle_list.append(self.listen_state(self.nest_changed, 'binary_sensor.nest_w1'))
    self.do_action()

  def nest_changed(self, entity, attribute, old, new, kwargs):
    self.do_action()

  def door_window_changed(self, entity, attribute, old, new, kwargs):
    self.do_action()

  def ha_panel_changed(self, entity, attribute, old, new, kwargs):
    self.do_action()

  def constraint_changed(self, entity, attribute, old, new, kwargs):
    self.do_action()

  def split_off(self):
    if self.split_state != "on" and self.split_state != "None":
        return
    remote = Remote()
    code = remote.set_mode("NONE", "NONE", 18, "OFF")
    self.call_service("mqtt/publish", topic = self.ir_topic, payload = code.decode("utf-8"))
    self.split_state = "off"
    if (self.timer != None):
        self.cancel_timer(self.timer)
    self.timer = self.run_in(self.run_in_split_off, 15)

  def run_in_split_off(self, args):
    self.turn_off("switch.plug_158d00010dd98d")

  def split_on(self, mode, temp):
    self.turn_on("switch.plug_158d00010dd98d")
    if (self.timer != None):
        self.cancel_timer(self.timer)
    self.timer = self.run_in(self.run_in_split_mode, 10, mode=mode, temp=temp, state="ON")

  def run_in_split_mode(self, args):
    code = ""
    self.log('mode: {}'.format(args['mode']))
    remote = Remote()
    code = remote.set_mode(args['mode'], "2", args['temp'], args['state'])
    code = code.decode("utf-8")
    self.call_service("mqtt/publish", topic = self.ir_topic, payload = code)
  
  def do_action(self):
    if 'constraint' in self.args and not self.constrain_input_boolean(self.args['constraint']):
        self.log("Temperature control is disabled.")
        self.split_off()
        return

    # Проверить alarm_panel
    ha_panel_state = self.get_state(self.args['ha_panel'])
    if (ha_panel_state != 'disarmed'):
        self.log("Nobody home. Turning off split.")
        self.split_off()
        return
    
    nest_target_cool = self.get_state('climate.living_room', attribute="temperature")
    nest_target_hot = nest_target_cool
    if nest_target_cool == None and nest_target_hot == None:
        nest_target_cool = self.get_state('climate.living_room', attribute="target_temp_high")
        nest_target_hot = self.get_state('climate.living_room', attribute="target_temp_low")

    nest_w1 = "off"
    nest_y1 = "off"

    nest_w1 = self.get_state('binary_sensor.nest_w1')
    nest_y1 = self.get_state('binary_sensor.nest_y1')

    if nest_y1 == "on":
        if self.check_door('FAN'):
            return
        self.split_state = "on"
        self.log("Turn on split for COOLING to {}.".format(nest_target_cool))
        self.split_on("COOLING", 16)

    elif nest_w1 == "on":
        if self.check_door('OFF'):
            return
        self.split_state = "on"
        self.log("Turn on split for HEATING to {}".format(nest_target_hot))
        self.split_on("HEATING", 28)

    else:
        self.log("Nest is reporting that temp is ok.")
        self.split_off()

  def terminate(self):
    if self.listen_event_handle_list != None:
      for listen_event_handle in self.listen_event_handle_list:
        self.cancel_listen_event(listen_event_handle)

  def check_door(self, mode):
    # Проверить датчики дверей и окон
    door_window_state = self.get_state(self.args['door_window'])
    if (door_window_state != 'off'):
        self.log("Balcony door is opened. Set split to fan mode.")
        if mode == "FAN":
            self.split_on("FAN", 16)
            return True
        else:
            self.split_off()
            return True
    return False

#
# App to control climate device (split system)
#
# Args:
#
# notify = notification platform to send notifications to
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

# -------------------------------------------------------------------------------------------------
"""
Library that genrates LG air conditioner remote codes
"""
FIRST_BYTE = 136 # b10001000

STATE = {
    "ON": 0,
    "OFF": 24, # b11000
    "CHANGE_MODE": 1,
}

MODE = {
    "HEATING": 4, # b100
    "AUTO": 3, # b011
    "FAN": 2, # b010
    "DEHUIDIFICATION": 1, # b001
    "COOLING": 0,
    "NONE": 0,
}

TEMPERATURE_OFFSET = 15

FAN = {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 4, # b100
    "NONE": 5, # b101
}

FIRST_HIGH = 8271
FIRST_LOW = 4298
ZERO_AND_ONE_HIGH = 439
ZERO_LOW = 647
ONE_LOW = 1709

BUFFER_SIZE = 59

def test_bit(num, offset):
    """
    Test the num(int) if at the given offset bit is 1
    """
    mask = 1 << offset
    return num & mask

def set_bit(num, offset):
    """
    Set bit to at the given offset to 1
    """
    mask = 1 << offset
    return num | mask

class Remote(object):
    """
    Library that genrates LG air conditioner remote codes
    """

    def __init__(self):
        self.codes = [0] * BUFFER_SIZE
        self.crc = 0

    def set_mode(self, mode, fan, temperature, state, jet=0):
        """
        Generate code and put it in the buffer
        """
        self.codes[0] = FIRST_HIGH
        self.codes[1] = FIRST_LOW
        self.crc = 0

        self.fill_buffer(0, 8, FIRST_BYTE)
        self.fill_buffer(8, 5, STATE[state])

        if state == 'OFF':
            self.fill_buffer(13, 3, MODE['NONE'])
        else:
            self.fill_buffer(13, 3, MODE[mode])

        if state == 'OFF':
            self.fill_buffer(16, 4, 0)
        else:
            self.fill_buffer(16, 4, temperature - TEMPERATURE_OFFSET)

        self.fill_buffer(20, 1, jet) # jet

        if state == 'OFF':
            self.fill_buffer(21, 3, FAN['NONE'])
        else:
            self.fill_buffer(21, 3, FAN[fan])

        self.fill_buffer(24, 4, self.crc)
        self.codes[BUFFER_SIZE - 1] = ZERO_AND_ONE_HIGH
        self.codes = binascii.hexlify(self.lirc2broadlink(self.codes))
        return self.codes

    def lirc2broadlink(self, pulses):
        array = bytearray()
     
        for pulse in pulses:
            pulse = int(pulse * 269 / 8192)  # 32.84ms units

            if pulse < 256:
                array += bytearray(struct.pack('>B', pulse))  # big endian (1-byte)
            else:
                array += bytearray([0x00])  # indicate next number is 2-bytes
                array += bytearray(struct.pack('>H', pulse))  # big endian (2-bytes)
     
        packet = bytearray([0x26, 0x00])  # 0x26 = IR, 0x00 = no repeats
        packet += bytearray(struct.pack('<H', len(array)))  # little endian byte count
        packet += array
        packet += bytearray([0x0d, 0x05])  # IR terminator
     
        # Add 0s to make ultimate packet size a multiple of 16 for 128-bit AES encryption.
        remainder = (len(packet) + 4) % 16  # rm.send_data() adds 4-byte header (02 00 00 00)
        if remainder:
            packet += bytearray(16 - remainder)
     
        return packet

    def fill_buffer(self, pos, bits, value):
        """
        Fill buffer
        """
        i = bits
        while i > 0:
            index = 2 + 2 * (pos + bits-i)
            self.codes[index] = ZERO_AND_ONE_HIGH

            if test_bit(value, i - 1) != 0:
                self.codes[index + 1] = ONE_LOW
            else:
                self.codes[index + 1] = ZERO_LOW

            if test_bit(value, i - 1) != 0:
                bitset = 0
                bitset = set_bit(bitset, (128 + i - pos - bits - 1) % 4)
                self.crc = self.crc + bitset

            i -= 1