import socket
import time
import math
import threading


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


QUIT = False


FUNCS = [
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
