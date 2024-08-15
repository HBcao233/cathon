from collections import namedtuple


Version = namedtuple('Version', ('major', 'minor', 'micro'))
version = Version(0, 0, 1)

def to_string():
  return '.'.join(map(str, version))
  