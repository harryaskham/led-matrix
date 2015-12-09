"""read some inputs from breadboard"""

import RPi.GPIO as GPIO
import time
import threading
import inputs

class Ticker(object):
  
  PIN = 19
  SENSITIVITY = 0.9

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.PIN, GPIO.OUT)
    self.sleep = 0.3
    self.pause = False

  def Start(self):
    def run():
      while True:
        while self.pause:
          time.sleep(1)
        GPIO.output(self.PIN, True)
        time.sleep(self.sleep)
        GPIO.output(self.PIN, False)
        time.sleep(self.sleep)

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




ticker = Ticker()
rot = inputs.RotaryEncoder(on_rotation=ticker.HandleSpeed, on_button=ticker.Pause)

ticker.Start()
raw_input('woop')
