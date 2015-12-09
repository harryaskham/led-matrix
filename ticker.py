"""read some inputs from breadboard"""

import RPi.GPIO as GPIO
import time
import threading
import inputs

class Ticker(object):

  PIN = 19
  SENSITIVITY = 0.9

  class Mode(object):
    LINEAR = 1
    SIN = 2

  def __init__(self, mode=Mode.LINEAR):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.PIN, GPIO.OUT)
    self.sleep = 0.3
    self.mode = mode
    self.pause = False

  def _GetSleepTime(self, t):
    if self.mode == Mode.LINEAR:
      return self.sleep
    if self.mode == Mode.SIN:
      return self.sleep * 0.5 * (math.sin(t / 10.0) + 1 + self.sleep)

  def Start(self):
    def run():
      t = 0
      while True:
        while self.pause:
          time.sleep(1)
        GPIO.output(self.PIN, True)
        time.sleep(self._GetSleepTime(t))
        GPIO.output(self.PIN, False)
        time.sleep(self._GetSleepTime(t))

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

  def HandleSpeed(self, clockwise):
    if clockwise:
      self.sleep *= self.SENSITIVITY
    else:
      self.sleep *= 1.0 / self.SENSITIVITY

  def Pause(self, down):
    if down:
      self.pause = not self.pause




ticker = Ticker(mode=Ticker.Mode.SIN)
rot = inputs.RotaryEncoder(on_rotation=ticker.HandleSpeed, on_button=ticker.Pause)

ticker.Start()
raw_input('woop')
