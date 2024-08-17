import argparse, sys, os
from . import errors, __version__
from .basic import run
from .shell import Shell


def run_code(file, code):
  try:
    res = run(file, code)
  except errors.BaseError as e:
    print(str(e))
    
  
def run_file(file):
  try:
    run(file.name, file.read())
  except errors.BaseError as e:
    print(str(e))
  

class ArgumentParser(argparse.ArgumentParser):
  def error(self, message=None):
    if message and message[9:message.find(':')] == '-c':
      print(_('Argument expected for the -c option'))
      print(_('usage') + ': ' + self.usage)
      print(_("Try") + " 'cathon -h' " + _("for more information."))
      self.exit(2)
    super().error(message)


def main():
  parser = ArgumentParser(
    prog='cathon',
    usage='cathon ' + _('[option] ... [-c cmd | -m mod | file | -] [arg] ...')
  )
  parser.add_argument('-v', '-V', '--version', action='version', version='%(prog)s ' + __version__)
  parser.add_argument('-c', dest='cmd')
  parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  
  args = parser.parse_args()
  if args.cmd is not None:
    run_code('<string>', args.cmd)
  elif not args.file.isatty():
    run_file(args.file)
  else:
    Shell()
  exit()


if __name__ == '__main__':
  main()
