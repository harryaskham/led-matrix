import socket
import time


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
  i = 0
  while True:
    for x in xrange(32):
      msg = [x]  # First entry is the strip number
      for y in xrange(32):
        msg += [255, i % 255, 255]
      Push([msg])
    time.sleep(.00005)
    i += 1
    

if __name__ == '__main__':
  Dance()
