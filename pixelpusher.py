import socket
from PIL import Image
import images2gif

import time
import math
import threading
import random
import numpy as np
from scipy import signal


UDP_IP = '192.168.0.16'
UDP_PORT = 5078


def Push(messages):
  for message in messages:
    message = ''.join(map(chr, message))  # Binary conversion
    sock = socket.socket(
        socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP
    bytes_sent = sock.sendto('    ' + message, (UDP_IP, UDP_PORT))


def SpinLines(x, y, t):
  return [abs(int(((x - 16) + (y - 16) * t) % 255)),
          int(abs(t / 2.0) % 255),
          int(127 * (math.sin(math.sqrt(t) * math.pi / 255) + 1))]


def MadTanStrobe(x, y, t):
  scale = 0.1
  return [int(abs(x - 16) * t * scale % 255),
          int(abs(y - 16) * (255/16) * math.cos(t * scale) % 255),
          int(math.tan(t * scale) % 255)]


def FastStrobe(x, y, t):
  return [255, 255, 255] if t % 2 == 0 else [0, 0, 0]

def SlowStrobe(x, y, t):
  return [255, 255, 255] if t % 4 == 0 else [0, 0, 0]

def SlowRedStrobe(x, y, t):
  return [255, 0, 0] if t % 4 == 0 else [0, 0, 0]

def SquareExpand(x, y, t):
  return [
    127 * (math.sin(y * t / 0.00001 + 3) + 1),
    127 * (math.cos(x * t / 0.00001 + 4) + 1),
    127 * (math.sin(t / 0.00001 + 5) + 1)]

def Random(x, y, t):
  return [int(255 * random.random()) for i in range(3)]


def Off(x, y, t):
  return [0, 0, 0]

def SetBrightness(l):
  def do_set(pixel):
    return [int(p * l) for p in pixel]
  return do_set

def Invert(pixel):
  return [255 - p for p in pixel]


class Led(object):

  def __init__(self, rgb, active=False):
    self.rgb = rgb
    self.active = active
    self.heat = 0

class Grid(object):

  def __init__(self):
    self.grid = [[Led([0, 0, 0]) for i in range(32)] for i in range(32)]

  def AtOffset(self, x, y, x_offset, y_offset):
    return self.grid[(y + y_offset) % 32][(x + x_offset) % 32]

  def GetActiveNeighbours(self, x, y):
    active = 0
    if self.AtOffset(x, y, -1, 0).active:
      active += 1
    if self.AtOffset(x, y, 1, 0).active:
      active += 1
    if self.AtOffset(x, y, 0, -1).active:
      active += 1
    if self.AtOffset(x, y, 0, 1).active:
      active += 1
    if self.AtOffset(x, y, -1, -1).active:
      active += 1
    if self.AtOffset(x, y, -1, 1).active:
      active += 1
    if self.AtOffset(x, y, 1, -1).active:
      active += 1
    if self.AtOffset(x, y, 1, 1).active:
      active += 1
    return active

  def Next(self):
    raise Exception


class Life(Grid):

  def __init__(self):
    Grid.__init__(self)
    self.grid[0][1].active = True
    self.grid[1][2].active = True
    self.grid[2][0].active = True
    self.grid[2][1].active = True
    self.grid[2][2].active = True
    self.grid[0][1].rgb = [255,255,255]
    self.grid[1][2].rgb = [255,255,255]
    self.grid[2][0].rgb = [255,255,255]
    self.grid[2][1].rgb = [255,255,255]
    self.grid[2][2].rgb = [255,255,255]
    for row in self.grid:
      for i, led in enumerate(row):
        if random.random() < 0.3:
          led.active = True
          led.rgb = [255, 255, 255]

  def Next(self):
    new_grid = [[Led([0, 0, 0]) for y in range(32)] for x in range(32)]
    for y, row in enumerate(self.grid):
      for x, led in enumerate(row):
        active_neighbours = self.GetActiveNeighbours(x, y)
        if (active_neighbours == 2 and self.grid[y][x].active or
            active_neighbours == 3):
          new_grid[y][x].active = True
          new_grid[y][x].rgb = [255, 255, 255]
        else:
          new_grid[y][x].active = False
    self.grid = new_grid


class Gif(Grid):

  def __init__(self, path):
    Grid.__init__(self)
    self.frame = 0
    self.frames = images2gif.readGif(path, False)
    [frame.thumbnail((32,32), Image.ANTIALIAS) for frame in self.frames]

  def Next(self):
    new_grid = [[Led([0, 0, 0]) for y in range(32)] for x in range(32)]
    frame = self.frames[self.frame]
    for y, row in enumerate(self.grid):
      for x, led in enumerate(row):
        pixel = frame.getpixel((x, y))
        led.rgb = pixel[-3:]
    self.frame = (self.frame + 1) % len(self.frames)


class Snake(Grid):

  def __init__(self):
    Grid.__init__(self)
    self.snake_pos = [(0, 0)]
    self.food_pos = (4, 4)

  def Draw(self):
    self.grid = [[Led([0, 0, 0]) for y in range(32)] for x in range(32)]
    for p in self.snake_pos:
      self.grid[p[1]][p[0]].rgb = [255, 255, 255]
    self.grid[self.food_pos[1]][self.food_pos[0]].rgb = [255, 0, 0]

  def Next(self):
    self.Draw()
    last_piece = self.MoveToFood()
    if self.food_pos in self.snake_pos:
      self.food_pos = (int(32 * random.random()), int(32 * random.random()))
      if last_piece:
        self.snake_pos.append(last_piece)

  def MoveToFood(self):
    direction = (self.snake_pos[0][0] - self.food_pos[0],
                 self.snake_pos[0][1] - self.food_pos[1])
    if direction == (0, 0):
      return

    if direction[0] < 0:
      self.snake_pos = (
          [(self.snake_pos[0][0]+1, self.snake_pos[0][1])] + self.snake_pos)
    elif direction[0] > 0:
      self.snake_pos = (
          [(self.snake_pos[0][0]-1, self.snake_pos[0][1])] + self.snake_pos)
    elif direction[1] < 0:
      self.snake_pos = (
          [(self.snake_pos[0][0], self.snake_pos[0][1]+1)] + self.snake_pos)
    elif direction[1] > 0:
      self.snake_pos = (
          [(self.snake_pos[0][0], self.snake_pos[0][1]-1)] + self.snake_pos)
    return self.snake_pos.pop()


class Tensors(Grid):

  def __init__(self):
    Grid.__init__(self)
    self.r = np.random.normal(size=[32, 32])
    self.g = np.random.normal(size=[32, 32])
    self.b = np.random.normal(size=[32, 32])

  def Next(self):
    self.UpdateTensors()
    for y, row in enumerate(self.grid):
      for x, led in enumerate(row):
        led.rgb = [
            50 * self.r[y][x] % 256,
            50 * self.g[y][x] % 256,
            50 * self.b[y][x] % 256]

  def UpdateTensors(self):
    r = self.g + 0.99 * self.b
    g = self.r - 0.99 * self.b
    b = self.g + 0.99 * self.r
    self.r, self.g, self.b = r, g, b


class GridDrawer(object):

  def __init__(self, grid, slowdown=1):
    self.last_t = 0
    self.grid = grid
    self.slowdown = slowdown

  def Run(self, x, y, t):
    if t / self.slowdown > self.last_t:
      self.last_t = t / self.slowdown
      self.grid.Next()
    return self.grid.grid[x][y].rgb


def Circle(x, y, t):
  scale = 0.01
  return [(math.pow(x-8+t/10, 2) + math.pow(y-8-t/10, 2)) % 256,
          int(60 * (math.cos(t * scale) + 1)),
          int(50 * (math.sin(t * scale) + 1))]


QUIT = False


FUNCS = [
   # (GridDrawer(Tensors()).Run, 1000),
    (GridDrawer(Gif('trippy.gif'), slowdown=2).Run, 300),
    (GridDrawer(Life(), slowdown=3).Run, 300),
    (GridDrawer(Gif('rotsq.gif')).Run, 300),
    (GridDrawer(Snake()).Run, 1000),
    (Random, 300),
    (Circle, 600),
    (GridDrawer(Gif('triangle.gif')).Run, 300),
    (SquareExpand, 600),
    (FastStrobe, 200),
    (GridDrawer(Gif('nyan.gif'), slowdown=3).Run, 300),
    (MadTanStrobe, 3000),
    (FastStrobe, 200),
    (SlowStrobe, 200),
    (SpinLines, 1000),
    (SlowRedStrobe, 400),
    (FastStrobe, 200),
]

MODS = [
    SetBrightness(1),
]


def Run():
  while True:
    for func, length in FUNCS:
      for t in range(length):
        if QUIT:
          return
        msgs = []
        for x in xrange(32):
          msg = [x]  # First entry is the strip number
          for y in xrange(32):
            pixel = func(x, y, t)
            for mod in MODS:
              pixel = mod(pixel)
            msg += pixel
          msgs.append(msg)
        Push(msgs)
        time.sleep(.01)



def TurnOff():
  for x in range(10):
    msgs = []
    for x in xrange(32):
      msg = [x]  # First entry is the strip number
      for y in xrange(32):
        msg += Off(x, y, t)
      msgs.append(msg)
    Push(msgs)
    time.sleep(.01)



if __name__ == '__main__':
  t = threading.Thread(target=Run)
  t.daemon = True
  t.start()
  raw_input("Press Enter to continue...")
  QUIT = True
  TurnOff()
