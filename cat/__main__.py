import sys, os
from getopt import getopt, GetoptError
from cmd import Cmd
from .basic import run
from . import version, errors
from .shell import Shell


def run_code(file, code):
  try:
    res = run(file, code)
  except errors.BaseError as e:
    print(str(e))
    
  
def run_file(file):
  try:
    with open(file) as f:
      code = f.read()
  except (Exception, SystemExit) as e:
    print(f"CatScript: can't open file '{os.path.realpath(file)}': [Errno 2] No such file or directory")
    return
  
  try:
    run(os.path.realpath(file), code)
  except errors.BaseError as e:
    print(str(e))
  
  
def main():
  try:
    opts, args = getopt(sys.argv[1:], 'vVhc:', ['version', 'help'])
    if len(opts) == 0 and len(args) == 0:
      Shell()
    else:
      if len(opts) > 0:
        for opt, val in opts:
          if opt == '-c':
            run_code('<string>', val)
            break
          elif opt in ('-h', '--help'):
            print('help')
          elif opt in ('-v', '--version'):
            print('CatScript ' + version.to_string())
      else:
        run_file(args[0])
  except GetoptError as e:
    if e.opt == 'c':
      print(f'Argument expected for the -{e.opt} option')
    else:
      print(f'Unknown option: -{e.opt}')
    print(f'usage: python -m cat [option] ... [-c cmd | -m mod | file | -] [arg] ...')
    print(f'Try `python -m cat -h` for more information.')
    sys.exit(2)
  
  
if __name__ == '__main__':
  main()