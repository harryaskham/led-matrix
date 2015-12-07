"""read some inputs from breadboard"""

import RPi.GPIO as GPIO
import time
import threading


class RotaryEncoder(object):

  A_PIN = 6  # Purple-green
  B_PIN = 12  # Orange-blue
  E_PIN = 13  # Brown-yellow

  PINS = [A_PIN, B_PIN, E_PIN]

  def __init__(self, on_rotation=None, on_button=None):
    self.on_rotation = on_rotation
    self.on_button = on_button

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.E_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(self.A_PIN, GPIO.FALLING, callback=self._HandleRotation)
    GPIO.add_event_detect(self.B_PIN, GPIO.FALLING, callback=self._HandleRotation)
    GPIO.add_event_detect(self.E_PIN, GPIO.BOTH, callback=self._HandleButton, bouncetime=200)

    self.a, self.b, _ = self._ReadPins()

  def _ReadPins(self):
    return [GPIO.input(pin) for pin in self.PINS]

  def _HandleRotation(self, pin):
    a, b, _ = self._ReadPins()
    c = a ^ b
    last_state = self.a*4 + self.b*2 + (self.a ^ self.b)
    new_state = a*4 + b*2 + c
    if last_state == new_state:
      return
    delta = (new_state - last_state) % 4
    self.a, self.b = a, b
    if self.on_rotation and (delta == 1 or delta == 3):
      self.on_rotation(clockwise=delta==1)

  def _HandleButton(self, pin):
    _, _, e = self._ReadPins()
    if self.on_button:
      self.on_button(down=e==0)
