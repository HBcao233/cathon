from typing import Any
from collections.abc import Iterable
from ..constants import *
from .position import Position


class Token(object):
  def __init__(self, type: str, value: Any = None, pos_start: Position = None, pos_end: Position = None):
    self.type = type
    self.value = value
    self.pos_start = pos_start.copy()
    if not pos_end:
      pos_end = pos_start
    self.pos_end = pos_end.copy()
    
  def __repr__(self):
    if self.value is None:
      return str(tok_name[self.type])
    return f'{tok_name[self.type]}({repr(self.value)})'
  
  def to_dict(self):
    if self.value is None:
      return {'type': tok_name[self.type]}
    return {'type': tok_name[self.type], 'value': self.value}
  
  def matches(self, type, values):
    if not isinstance(values, Iterable):
      values = (values,)
    return self.type == type and any(self.value == value for value in values)
