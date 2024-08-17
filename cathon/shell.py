import re, string, sys, os, atexit
from . import errors, __version__
from .basic import run
from .constants import BUILTINS, KEYWORDS
from .interpreter import values

__all__ = ["Shell"]

PROMPT = '>>> '
MULTI_PROMPT = '... '
IDENTCHARS = string.ascii_letters + string.digits + '_'
newline_pattern = re.compile(r'(:|\(|\[|\{|\\)$').search


class Shell:
  prompt = PROMPT
  identchars = IDENTCHARS
  intro = 'Welcome to Cathon ' + __version__

  def __init__(self):
    self.stdin = sys.stdin
    self.stdout = sys.stdout
    self.cmdqueue = []
    self.histfile = os.path.expanduser("~/.cat_history")
    
    try:
      import readline
      if not os.path.isfile(self.histfile):
        open(self.histfile, 'w').close()
      self.old_completer = readline.get_completer()
      readline.set_completer(self.complete)
      readline.parse_and_bind("tab: complete")
      try:
        readline.read_history_file(self.histfile)
        self.hlen = readline.get_current_history_length()
      except FileNotFoundError:
        self.hlen = 0
      atexit.register(self.save_history)
    except ImportError:
      pass
   
    self.stdout.write(str(self.intro)+"\n")
    while True:
      try:
        line = input(self.prompt)
      except KeyboardInterrupt:
        self.stdout.write("\nKeyboardInterrupt\n")
        self.prompt = PROMPT
        self.cmdqueue = []
        continue
      except EOFError:
        self.stdout.write("\n")
        sys.exit(0)
        
      if self.prompt != MULTI_PROMPT:
        if newline_pattern(line):
          self.prompt = MULTI_PROMPT
          self.cmdqueue.append(line)
      else:
        if line:
          self.cmdqueue.append(line)
        else:
          self.prompt = PROMPT
          line = '\n'.join(self.cmdqueue) + '\n'
          self.cmdqueue = []
      if self.prompt != MULTI_PROMPT:
        self.main(line)
      
  def main(self, line):
    try:
      res = run('<stdin>', line).get_object()
      if len(res):
        if len(res) == 1:
          if res[0] is not values.null:
            print(repr(res[0]))
        else:
          print(repr(res))
    except errors.BaseError as e:
      print(str(e))
    
  def save_history(self):
    import readline
    readline.set_completer(self.old_completer)
    readline.set_history_length(1000)
    readline.append_history_file(readline.get_current_history_length() - self.hlen, self.histfile)

  def parseline(self, line):
    line = line.strip()
    if not line:
        return None, None, line
    elif line[0] == '?':
        line = 'help ' + line[1:]
    elif line[0] == '!':
        if hasattr(self, 'do_shell'):
            line = 'shell ' + line[1:]
        else:
            return None, None, line
    i, n = 0, len(line)
    while i < n and line[i] in self.identchars: i = i+1
    cmd, arg = line[:i], line[i:].strip()
    return cmd, arg, line

  def completedefault(self, *ignored):
    return BUILTINS | KEYWORDS

  def completenames(self, text, *ignored):
    return [i for i in BUILTINS | KEYWORDS if i.startswith(text)]

  def complete(self, text, state):
    if state == 0:
      import readline
      origline = readline.get_line_buffer()
      line = origline.lstrip()
      stripped = len(origline) - len(line)
      begidx = readline.get_begidx() - stripped
      endidx = readline.get_endidx() - stripped
      if begidx > 0:
        cmd, args, foo = self.parseline(line)
        if cmd == '':
          compfunc = self.completedefault
        else:
          try:
            compfunc = getattr(self, 'complete_' + cmd)
          except AttributeError:
            compfunc = self.completedefault
      else:
        compfunc = self.completenames
      self.completion_matches = compfunc(text, line, begidx, endidx)
    try:
      return self.completion_matches[state]
    except IndexError:
      return None
