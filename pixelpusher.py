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


def Off(x, y, t):
  return [0, 0, 0]


QUIT = False


def Run():
  t = 0
  while not QUIT:
    msgs = []
    for x in xrange(32):
      msg = [x]  # First entry is the strip number
      for y in xrange(32):
        if t % 2000 < 1000:
          msg += SpinLines(x, y, t)
        elif t % 2000 < 2000
          msg += MadTanStrobe(x, y, t)
      msgs.append(msg)
    Push(msgs)
    time.sleep(.01)
    t += 1



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
