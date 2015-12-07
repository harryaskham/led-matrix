"""Modification of the sparkfruit example python to support 32x32 and D pin."""

import RPi.GPIO as GPIO
import time
import threading
import random
import math


def BitsFromInt(x):
    a_bit = x & 1
    b_bit = x & 2
    c_bit = x & 4
    d_bit = x & 8
    return (a_bit, b_bit, c_bit, d_bit)


class LedMatrix(object):
  """controller class for the 32x32 matrix"""
  DIM = 32
  DELAY = 0.0000001
  PWM_BITS = 8

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    self.red1_pin = 11
    self.green1_pin = 27
    self.blue1_pin = 7
    self.red2_pin = 8
    self.green2_pin = 9
    self.blue2_pin = 10
    self.clock_pin = 17
    self.a_pin = 22
    self.b_pin = 23
    self.c_pin = 24
    self.d_pin = 25
    self.latch_pin = 4
    self.oe_pin = 18

    GPIO.setup(self.red1_pin, GPIO.OUT)
    GPIO.setup(self.green1_pin, GPIO.OUT)
    GPIO.setup(self.blue1_pin, GPIO.OUT)
    GPIO.setup(self.red2_pin, GPIO.OUT)
    GPIO.setup(self.green2_pin, GPIO.OUT)
    GPIO.setup(self.blue2_pin, GPIO.OUT)
    GPIO.setup(self.clock_pin, GPIO.OUT)
    GPIO.setup(self.a_pin, GPIO.OUT)
    GPIO.setup(self.b_pin, GPIO.OUT)
    GPIO.setup(self.c_pin, GPIO.OUT)
    GPIO.setup(self.d_pin, GPIO.OUT)
    GPIO.setup(self.latch_pin, GPIO.OUT)
    GPIO.setup(self.oe_pin, GPIO.OUT)

    self.screen = [[[0, 0, 0] for x in xrange(32)] for x in xrange(32)]
    self.scan_i = 0
    self.quit = False

  def Clock(self):
    GPIO.output(self.clock_pin, 1)
    GPIO.output(self.clock_pin, 0)

  def Latch(self):
    GPIO.output(self.latch_pin, 1)
    GPIO.output(self.latch_pin, 0)

  def SetRow(self, row):
    a_bit, b_bit, c_bit, d_bit = BitsFromInt(row)
    GPIO.output(self.a_pin, a_bit)
    GPIO.output(self.b_pin, b_bit)
    GPIO.output(self.c_pin, c_bit)
    GPIO.output(self.d_pin, d_bit)

  def GetRgbBits(self, rgb):
    return [(self.scan_i % self.PWM_BITS) * (256 / self.PWM_BITS) < p for p in rgb]

  def SetColorTop(self, rgb):
    r, g, b = self.GetRgbBits(rgb)
    GPIO.output(self.red1_pin, r)
    GPIO.output(self.green1_pin, g)
    GPIO.output(self.blue1_pin, b)

  def SetColorBottom(self, rgb):
    r, g, b = self.GetRgbBits(rgb)
    GPIO.output(self.red2_pin, r)
    GPIO.output(self.green2_pin, g)
    GPIO.output(self.blue2_pin, b)

  def Refresh(self):
    for row in range(self.DIM / 2):
      self.SetRow(row)
      for i in range(self.PWM_BITS):  #pwm hack
        GPIO.output(self.oe_pin, 1)
        for col in range(self.DIM):
          self.SetColorTop(self.screen[row][col])
          self.SetColorBottom(self.screen[row+self.DIM/2][col])
          self.Clock()
        self.Latch()
        GPIO.output(self.oe_pin, 0)
        self.scan_i += 1
      time.sleep(self.DELAY)

  def FillRect(self, x1, y1, x2, y2, rgb):
    for x in range(x1, x2):
      for y in range(y1, y2):
        self.screen[y][x] = rgb

  def SetPixel(self, x, y, rgb):
    self.screen[y][x] = rgb

  def Start(self):
    print 'Starting LED matrix'
    def run():
      while not self.quit:
        self.Refresh()
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

  def Stop(self):
    print 'Stopping LED matrix'
    self.quit = True
    time.sleep(0.5)
    self.FillRect(0, 0, 32, 32, [0, 0, 0])
    self.Refresh()
    GPIO.cleanup()


def main():
  m = LedMatrix()
  m.FillRect(0, 0, 10, 10, [255, 0, 0])
  m.FillRect(20, 23, 27, 30, [0, 255, 0])
  m.SetPixel(4, 4, [0, 0, 255])
  m.Start()

  def DrawLoop():
    t = 0
    while True:
      for y in range(32):
        for x in range(32):
          m.SetPixel(x, y, [(x * 255) / 32, (y * 255) / 32, 255])
      time.sleep(0.1)
      t += 1

  t = threading.Thread(target=DrawLoop)
  t.daemon = True
  t.start()

  raw_input('enter quits')
  m.Stop()


main()
