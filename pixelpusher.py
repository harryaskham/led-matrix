import socket
import time
import math


UDP_IP = '127.0.0.1'
UDP_PORT = 5078


def Push(messages):
  for message in messages:
    message = ''.join(map(chr, message))  # Binary conversion
    sock = socket.socket(
        socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP
    bytes_sent = sock.sendto('    ' + message, (UDP_IP, UDP_PORT))

def Dance():
  t = 0.0
  while True:
    for x in xrange(32):
      msg = [x]  # First entry is the strip number
      for y in xrange(32):
        msg += [int(127 * (math.sin(t) + 1)),
                int(127 * (math.cos(t) + 1)),
                int(127 * (math.sin(t * t) + 1))]
      Push([msg])
    time.sleep(.00005)
    t += 0.01
    

if __name__ == '__main__':
  Dance()
