import re
from .lexer.position import Position
from .interpreter.context import Context


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
    compensate = len(re.sub(r'[\u0000-\u007F]', '', line[:pos_start.column]))
    
    column_start = len(line) if i < error_line_idx_start else error_pos_start.column
    column_end = error_pos_end.column if i == error_line_idx_end else len(line) - 1
    res.append('    ' + line)
    arrow_count = column_end - column_start
    if i == error_line_idx_end:
      if arrow_count <= 0:
        arrow_count = 1
    if arrow_count > 0:
      res.append('    ' + ' ' * (column_start + compensate) + '^' * arrow_count)
    idx_start = idx_end
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
      idx_end = len(text)
  return '\n'.join(res)
  

class BaseError(Exception):
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
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_name: str = 'Runtime Error', error_pos_start=None,  error_pos_end=None):
    self.context = context
    super().__init__(pos_start, pos_end, error_name, details, error_pos_start, error_pos_end)

  def __str__(self):
    return (
      self.generate_traceback() + '\n' +
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
    return '\n'.join(res[::-1])


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


class KeyError(RuntimeError):
  def __init__(self, pos_start, pos_end, details: str, context: Context, error_pos_start=None,  error_pos_end=None):
    super().__init__(pos_start, pos_end, details, context, 'KeyError', error_pos_start,  error_pos_end)
