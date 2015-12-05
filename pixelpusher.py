import socket
import time
import math
import threading
import random


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

class Grid(object):

  def __init__(self):
    self.grid = [[Led([0, 0, 0]) for i in range(32)] for i in range(32)]


class Life(Grid):

  def __init__(self):
    Grid.__init__(self)
    for row in self.grid:
      for i, led in enumerate(row):
        if random.random() > 0.03:
          led.active = True
          led.rgb = [255, 255, 255]

  def GetActiveNeighbours(self, x, y):
    active = 0
    if x - 1 >= 0 and self.grid[y][x-1].active:
      active += 1
    if x + 1 <= 31 and self.grid[y][x+1].active:
      active += 1
    if y - 1 >= 0 and self.grid[y-1][x].active:
      active += 1
    if y + 1 <= 31 and self.grid[y+1][x].active:
      active += 1
    if x - 1 >= 0 and y - 1 >= 0 and self.grid[y-1][x-1].active:
      active += 1
    if x - 1 >= 0 and y + 1 <= 31 and self.grid[y+1][x-1].active:
      active += 1
    if x + 1 <= 31 and y - 1 >= 0 and self.grid[y-1][x+1].active:
      active += 1
    if x + 1 <= 31 and y + 1 <= 31 and self.grid[y+1][x+1].active:
      active += 1
    return active

  def Next(self):
    new_grid = [[Led([0, 0, 0]) for i in range(32)] for i in range(32)]
    for y, row in enumerate(self.grid):
      for x, led in enumerate(row):
        active_neighbours = self.GetActiveNeighbours(x, y)
        if active_neighbours < 2 or active_neighbours > 4:
          new_grid[y][x].active = False
          new_grid[y][x].rgb = [0, 0, 0]
        else:
          new_grid[y][x].active = True
          new_grid[y][x].rgb = [255, 255, 255]
    self.grid = new_grid


last_t = 0
def GridDrawer(grid):
  def run(x, y, t):
    global last_t
    slowdown = 3
    if t / slowdown > last_t:
      last_t = t / slowdown
      grid.Next()
    return grid.grid[y][x].rgb
  return run
    

QUIT = False


FUNCS = [
    (GridDrawer(Life()), 10000),
    (SquareExpand, 1000),
    (FastStrobe, 200),
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
