import argparse
import sys
from . import __version__
from .basic import run, deparse
from .shell import Shell


class ArgumentParser(argparse.ArgumentParser):
  def error(self, message=None):
    if message and message[9 : message.find(':')] == '-c':
      print('Argument expected for the -c option')
      print('usage' + ': ' + self.usage)
      print('Try' + " 'cathon -h' " + 'for more information.')
      self.exit(2)
    super().error(message)


def main():
  parser = ArgumentParser(
    prog='cathon',
    usage='cathon [option] ... [-c cmd | -m mod | file | -o [deparse_output]] [arg] ...',
  )
  parser.add_argument(
    '-v', '-V', '--version', action='version', version='%(prog)s ' + __version__
  )
  parser.add_argument('-c', dest='cmd')
  parser.add_argument(
    '-o',
    '--output',
    dest='output',
    nargs='?',
    help='输出为python',
    type=argparse.FileType('w'),
    const=sys.stdout,
    default=None,
  )
  parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

  args = parser.parse_args()

  if args.cmd is not None:
    if args.output is not None:
      deparse('<string>', args.cmd, args.output)
    else:
      res = run('<string>', args.cmd)
      print(res)
  elif not args.file.isatty():
    if args.output is not None:
      deparse(args.file.name, args.file.read(), args.output)
    else:
      run(args.file.name, args.file.read())
  else:
    Shell()


if __name__ == '__main__':
  main()
