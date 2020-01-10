import appdaemon.plugins.hass.hassapi as hass
import datetime
import random
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

class XmasTreeTimer(hass.Hass):
  effects = []
  def initialize(self):
    self.effects = ['[FX=00] Solid',
                  '[FX=01] Blink',
                  '[FX=02] Breathe',
                  '[FX=03] Wipe',
                  '[FX=04] Wipe Random',
                  '[FX=05] Random Colors',
                  '[FX=06] Sweep',
                  '[FX=07] Dynamic',
                  '[FX=08] Colorloop',
                  '[FX=09] Rainbow',
                  '[FX=10] Scan',
                  '[FX=11] Dual Scan',
                  '[FX=12] Fade',
                  '[FX=13] Chase',
                  '[FX=14] Chase Rainbow',
                  '[FX=15] Running',
                  '[FX=16] Saw',
                  '[FX=17] Twinkle',
                  '[FX=18] Dissolve',
                  '[FX=19] Dissolve Rnd',
                  '[FX=20] Sparkle',
                  '[FX=21] Dark Sparkle',
                  '[FX=22] Sparkle+',
                  '[FX=23] Strobe',
                  '[FX=24] Strobe Rainbow',
                  '[FX=25] Mega Strobe',
                  '[FX=26] Blink Rainbow',
                  '[FX=27] Android',
                  '[FX=28] Chase',
                  '[FX=29] Chase Random',
                  '[FX=30] Chase Rainbow',
                  '[FX=31] Chase Flash',
                  '[FX=32] Chase Flash Rnd',
                  '[FX=33] Rainbow Runner',
                  '[FX=34] Colorful',
                  '[FX=35] Traffic Light',
                  '[FX=36] Sweep Random',
                  '[FX=37] Running 2',
                  '[FX=38] Red & Blue',
                  '[FX=39] Stream',
                  '[FX=40] Scanner',
                  '[FX=41] Lighthouse',
                  '[FX=42] Fireworks',
                  '[FX=43] Rain',
                  '[FX=44] Merry Christmas',
                  '[FX=45] Fire Flicker',
                  '[FX=46] Gradient',
                  '[FX=47] Loading',
                  '[FX=48] In Out',
                  '[FX=49] In In',
                  '[FX=50] Out Out',
                  '[FX=51] Out In',
                  '[FX=52] Circus',
                  '[FX=53] Halloween',
                  '[FX=54] Tri Chase',
                  '[FX=55] Tri Wipe',
                  '[FX=56] Tri Fade',
                  '[FX=57] Lightning',
                  '[FX=58] ICU',
                  '[FX=59] Multi Comet',
                  '[FX=60] Dual Scanner',
                  '[FX=61] Stream 2',
                  '[FX=62] Oscillate',
                  '[FX=63] Pride 2015',
                  '[FX=64] Juggle',
                  '[FX=65] Palette',
                  '[FX=66] Fire 2012',
                  '[FX=67] Colorwaves',
                  '[FX=68] BPM',
                  '[FX=69] Fill Noise',
                  '[FX=70] Noise 1',
                  '[FX=71] Noise 2',
                  '[FX=72] Noise 3',
                  '[FX=73] Noise 4',
                  '[FX=74] Colortwinkle',
                  '[FX=75] Lake',
                  '[FX=76] Meteor',
                  '[FX=77] Smooth Meteor',
                  '[FX=78] Railway',
                  '[FX=79] Ripple',
                  '[FX=80] Twinklefox',
                  '[FX=81] Twinklecat',
                  '[FX=82] Halloween Eyes']
    # self.effects = ['FX=00','FX=01','FX=02']
    # self.on_timer = self.run_every(self.on_timer_tick, on_time)
    # self.off_timer = self.run_daily(self.off_timer_tick, off_time)
    self.run_every(self.run_every_c, datetime.datetime.now(), 15)

  def run_every_c(self, kwargs):
    effect = random.choice(self.effects)
    # rand = random.randint(0, 82)
    # effect = "FX={}".format(rand)
    self.log('random: {}'.format(effect))
    self.call_service("mqtt/publish", topic = 'wled/d85df2/api', payload = effect)
