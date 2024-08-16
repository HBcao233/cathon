import re
from .lexer.position import Position
from .interpreter.context import Context


widths = [
  (126,    1), (159,    0), (687,     1), (710,   0), (711,   1), 
  (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0), 
  (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1), 
  (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2), 
  (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
  (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
  (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
  (120831, 1), (262141, 2), (1114109, 1),
]

def char_width(o: int) -> int:
  """Return the screen column width for unicode ordinal o."""
  global widths
  if o == 0xe or o == 0xf:
    return 0
  for num, wid in widths:
    if o <= num:
      return wid
  return 1
    
    
def str_width(s: str) -> int:
  res = 0
  for i in s:
    res += char_width(ord(i))
  return res
  

def _string_with_arrows(text, pos_start, pos_end, error_pos_start=None, error_pos_end=None):
  if error_pos_start is None:
    error_pos_start = pos_start
  if error_pos_end is None:
    error_pos_end = pos_end
    
  res = []
  idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
  idx_end = text.find('\n', idx_start + 1)
  if idx_end < 0:
    idx_end = len(text)
  line_count = pos_end.line - pos_start.line + 1
  error_line_idx_start = error_pos_start.line - pos_start.line
  error_line_idx_end = error_pos_end.line - pos_start.line 
  
  for i in range(line_count):
    line = text[idx_start:idx_end].strip('\n')
    before_text = line[:pos_start.column]
    space_count = str_width(before_text)
    
    column_start = len(line) if i < error_line_idx_start else error_pos_start.column
    column_end = error_pos_end.column if i == error_line_idx_end else len(line) - 1
    
    error_text = line[column_start:column_end]
    arrow_count = str_width(error_text)
    if i == error_line_idx_end:
      if arrow_count <= 0:
        arrow_count = 1
        
    res.append('    ' + line)
    if arrow_count > 0:
      res.append('    ' + ' ' * space_count + '^' * arrow_count)
    
    idx_start = idx_end
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
      idx_end = len(text)
  return '\n'.join(res)
  

class BaseError(Exception):
  ATTR__name__ = 'BaseException'
  
  def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str, error_pos_start=None,  error_pos_end=None):
    self.pos_start = pos_start.copy()
    self.pos_end = pos_end.copy()
    self.error_name = error_name
    self.details = details
    self.error_pos_start = error_pos_start
    self.error_pos_end = error_pos_end
    
  def __str__(self):
    return (
      f'  File "{self.pos_start.file}", line {self.pos_end.line + 1}\n' + 
      _string_with_arrows(self.pos_start.code, self.pos_start, self.pos_end, self.error_pos_start, self.error_pos_end) + '\n'
      f'{self.error_name}: {self.details}\n'
    )


class InvalidAtom(BaseError):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'InvalidAtom', details)


class TabError(BaseError):
  def __init__(self, pos_start, pos_end, details: str):
    super().__init__(pos_start, pos_end, 'TabError', details)
    
    
class SyntaxError(BaseError):
  def __init__(self, pos_start, pos_end, details: str = 'invalid syntax', error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, 'SyntaxError', details, error_pos_start, error_pos_end)


class IndentationError(BaseError):
  def __init__(self, pos_start, pos_end, details: str, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, 'IndentationError', details, error_pos_start, error_pos_end)


class RuntimeError(BaseError):
  def __init__(self, 
    pos_start, pos_end, 
    details: str, 
    context: Context, 
    error_name: str = 'RuntimeError', 
    error_pos_start=None,  error_pos_end=None,
  ):
    self.context = context
    super().__init__(pos_start, pos_end, error_name, details, error_pos_start, error_pos_end)

  def __str__(self):
    return (
      self.generate_traceback() +
      _string_with_arrows(self.pos_start.code, self.pos_start, self.pos_end, self.error_pos_start, self.error_pos_end) + '\n' + 
      f'{self.error_name}: {self.details}\n'
    )
    
  def generate_traceback(self):
    res = []
    pos = self.pos_start
    ctx = self.context
    while ctx:
      res.append(f'  File "{pos.file}", line {pos.line + 1}, in {ctx.display_name}')
      pos = ctx.parent_pos
      ctx = ctx.parent
    res.append('Traceback (most recent call last):')
    return '\n'.join(res[::-1]) + '\n'


class OpertionError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'OpertionError', error_pos_start, error_pos_end)


class NameError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'NameError', error_pos_start, error_pos_end)
    

class TypeError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'TypeError', error_pos_start, error_pos_end)


class IndexError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'IndexError', error_pos_start,  error_pos_end)


class AttributeError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'AttributeError', error_pos_start,  error_pos_end)
    

class KeyError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'KeyError', error_pos_start,  error_pos_end)
