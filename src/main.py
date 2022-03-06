from getopt import getopt, GetoptError
from sys import argv, exit
from signal import signal, SIGINT, SIGTERM
from honeypot import Honeypot

honeypot = None

def signal_stop(sig, frame):
  """
  signal_stop(signal, frame) -> None

  Kill all subprocess and stop script
  """
  honeypot.stop()
  exit(2)


def findArg(name, opts, default_value=None):
  """
  findArg(name, opts, default_value) -> Argument value | default_value
  
  Return given argument value for given name
  """
  try:
    value = [item for item in opts if name in item].pop()
    return value[-1]
  except Exception:
    return default_value

# register signals to stop script
signal(SIGINT, signal_stop)
signal(SIGTERM, signal_stop)

try:
  opts, args = getopt(argv[1:], 'a:p:')
except GetoptError:
  print('main.py [-a address] [-p port]')
  exit(2)

address = findArg('-a', opts, 'localhost')
port = findArg('-p', opts, 8080)

honeypot = Honeypot(address, port)
honeypot.run()
