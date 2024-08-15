import math
from abc import ABC, abstractmethod 
from ..constants import *
from .. import errors
from .context import Context


def need_implemente_method(method_name):
  def wrappered_method(self, *args, **kwargs):
    print('a')
    if method_name not in self.__class__.__dict__:
      raise errors.TypeError(
        self.pos_start, self.pos_end, 
        f"bad operand type for {method_name.replace('_', '')}(): '{self.name}'", self.context
      )
    return self.__class__.__getattr__(method_name)(self, *args, **kwargs)
  wrappered_method.__name__ = method_name
  wrappered_method.__qualname__ = 'Value.'+method_name
  return wrappered_method
  
  
class Value(ABC):
  name = '<anonymous>'
  __abs__ = need_implemente_method('__abs__')
  
  def __init__(self):
    self.set_pos()
    self.set_context()
    
  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self
    
  def set_context(self, context: Context = None):
    self.context = context
    return self
    
  def __str__(self):
    val = self.get_object()
    if val is None:
      return 'null'
    if val is True:
      return 'true'
    if val is False:
      return 'false'
    return str(val)
    
  def __repr__(self):
    val = self.get_object()
    if val is None:
      return 'null'
    if val is True:
      return 'true'
    if val is False:
      return 'false'
    return repr(val)
    
  def get_object(self):
    raise NotImplementedError
  
  def get_pyobject(self):
    return self.get_object()
    
  def __pos__(self):
    return +(self.get_object())
    
  def __neg__(self):
    return -(self.get_object())
    
  def __invert__(self):
    return ~(self.get_object())
  
  def __pow__(self, other):
    return self.get_object() ** other.get_object()
    
  def __add__(self, other):
    return self.get_object() + other.get_object()
  
  def __sub__(self, other):
    return self.get_object() - other.get_object()
    
  def __mul__(self, other):
    return self.get_object() * other.get_object()
    
  def __truediv__(self, other):
    return self.get_object() / other.get_object()
  
  def __floordiv__(self, other):
    return self.get_object() // other.get_object()
  
  def __mod__(self, other):
    return self.get_object() % other.get_object()
    
  def __and__(self, other):
    return self.get_object() & other.get_object()
  
  def __or__(self, other):
    return self.get_object() | other.get_object()
  
  def __xor__(self, other):
    return self.get_object() ^ other.get_object()
  
  def __lshift__(self, other):
    return self.get_object() << other.get_object()
    
  def __rshift__(self, other):
    return self.get_object() >> other.get_object()
  
  def __bool__(self):
    return False 
    
  def __hash__(self):
    return hash(self.get_object())

  def __eq__(self, other):
    if not isinstance(other, Value):
      return False
    return self.name == other.name
    
  def __lt__(self, other):
    return self.get_object() < other.get_object()
    
  def __le__(self, other):
    return any(i(other) for i in (self.__lt__, self.__eq__))
    
  def invalid(self, op, other=None, details=None):
    if details is None:
      details = f'invalid operation: {op} (between {self.name} and {other.name})'
    raise errors.OpertionError(
      self.pos_start, self.pos_end,
      details, self.context, 
    )
    
  def unary_op(self, op):
    try:
      if op == PLUS:
        return +self
      if op == MINUS:
        return -self
      if op == TILDE:
        return ~self
      if op == EXCLAMATION:
        return not self 
    except TypeError:
      return self.invalid(op, details=f'invalid unary operation: {OP_REDICT[op]} (to {self.name})')
    return self.invalid(op, details=f'invalid unary operation: {OP_REDICT[op]}')
  
  def binary_op(self, op, other):
    if not isinstance(other, Value):
      return self.invalid(op, details=f'invalid unary operation: {op} (to {self})')
    
    try:
      if op == DOUBLESTAR:
        return self ** other
      if op == STAR:
        return self * other
      if op == SLASH:
        return self / other
      if op == DOUBLESLASH:
        return self // other
      if op == PERCENT:
        return self % other
      if op == PLUS:
        return self + other
      if op == MINUS:
        return self - other
      if op == DOUBLEAMPER:
        return self and other
      if op == DOUBLEVBAR:
        return self or other
      if op == AMPER:
        return self & other
      if op == VBAR:
        return self | other
      if op == CIRCUMFLEX:
        return self ^ other
      if op == LEFTSHIFT:
        return self << other
      if op == RIGHTSHIFT:
        return self >> other
      if op == EQEQUAL:
        return self == other
      if op == NOTEQUAL:
        return self != other
      if op == LESS:
        return self < other
      if op == GREATER:
        return self > other
      if op == LESSEQUAL:
        return self <= other
      if op == GREATEREQUAL:
        return self >= other
      if op == AT:
        return self @ other
    except TypeError:
      return self.invalid(op, other, details=f"'{OP_REDICT[op]}' not supported between instances of '{self.name}' and '{other.name}'")
    return self.invalid(op, other, details=f'invalid binary operation: {OP_REDICT[op]}')
  
  @abstractmethod
  def copy(self):
    return Value().set_pos(self.pos_start, self.pos_end).set_context(self.context)


class Single(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
  
  def copy(self):
    return Single(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
  
  def get_object(self):
    return self.value
  
  def __bool__(self):
    return bool(self.value)
    
  def __hash__(self):
    return super().__hash__()
  
  def __eq__(self, other):
    return self.name == other.name and self.get_object() == other.get_object()
  

class Number(Single):
  name = 'number'
  def __init__(self, value):
    super().__init__(value)
    if isinstance(value, bool):
      self.name = 'bool'
    elif isinstance(value, int):
      self.name = 'int'
    elif isinstance(value, float):
      self.name = 'float'
    else:
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"can't convert \"{value}\" to a nunber", self.context, 
      )
      
  def zero_error(self):
    raise errors.OpertionError(
      self.pos_start, self.pos_end,
      'division by zero', self.context, 
    )
    
  def copy():
    return Number(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
    
  def __hash__(self):
    return super().__hash__()
    
  def __truediv__(self, other):
    if other.get_object() == 0:
      return self.zero_error()
    return super().__div__(other)
    
  def __floordiv__(self, other):
    if other.get_object() == 0:
      return self.zero_error()
    return super().__floor__(other)
    
  def __eq__(self, other):
    return self.get_object() == other.get_object()
  
  def bool_to_string(self):
    return 'true' if self.get_object() else 'false'
    
  def __str__(self):
    if self.name == 'bool':
      return self.bool_to_string()
    if self.name == 'float':
      if self.get_object() == float('-inf'):
        return '-Inf'
      if self.get_object() == float('inf'):
        return 'Inf'
      if math.isnan(self.get_object()):
        return 'NaN'
    return str(self.value)
    
  def __repr__(self):
    if self.name == 'bool':
      return self.bool_to_string()
    if self.name == 'float':
      if self.get_object() == float('-inf'):
        return '-Inf'
      if self.get_object() == float('inf'):
        return 'Inf'
      if math.isnan(self.get_object()):
        return 'NaN'
    return repr(self.value)
  
  def __abs__(self):
    return abs(self.value)


class String(Single):
  name = 'str'
  def copy():
    return String(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
  
  def __hash__(self):
    return hash(self.value)
    
  def __getitem__(self, key):
    if not isinstance(key, int) and key.name not in ('int', 'slice'):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"string indices must be integers or slices, not {key.name}", self.context, 
      )
    try:
      if isinstance(key, int):
        return self.get_object().__getitem__(key)
      return self.get_object().__getitem__(key.get_object())
    except IndexError as e:
      if isinstance(key, int):
        raise
      raise errors.IndexError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )
    

class Null(Single):
  name = 'null'
  def __init__(self):
    super().__init__(None)
  
  def __str__(self):
    return 'null'
    
  def __repr__(self):
    return 'null'
    
  def get_object(self):
    return None
  
  def __and__(self, other):
    raise TypeError
  
  def __hash__(self):
    return hash(None)
  
  def __eq__(self, other):
    if isinstance(other, Null): 
      return True
    return NotImplemented


true = Number(True)
false = Number(False)
null = Null()


class List(Value):
  name = 'list'
  def __init__(self, items):
    super().__init__()
    self.items = items
  
  def get_object(self):
    return self.items
    
  def get_pyobject(self):
    return [i.get_object() for i in self.items]
  
  def copy(self):
    return List(self.items).set_pos(self.pos_start, self.pos_end).set_context(self.context)
  
  def __len__(self):
    return len(self.items)
    
  def __iter__(self):
    return iter(self.items)
  
  def __getitem__(self, key):
    if key.name not in ('int', 'slice'):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"list indices must be integers or slices, not {key.name}", self.context, 
      )
    try:
      return self.get_object().__getitem__(key.get_object())
    except IndexError as e:
      raise errors.IndexError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )
      
  def __setitem__(self, key, value):
    if key.name not in ('int', 'slice'):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"string indices must be integers or slices, not {key.name}", self.context, 
      )
    
    try:
      return self.get_object().__setitem__(key.get_object(), value)
    except IndexError as e:
      raise errors.IndexError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )
    except TypeError as e:
      raise errors.TypeError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )


class Dict(Value):
  name = 'dict'
  def __init__(self, items: dict):
    super().__init__()
    self._items = items
  
  def get_object(self):
    return self._items
    
  def get_pyobject(self):
    return {k.get_object(): v.get_object() for k, v in self._items.items()}
  
  def copy(self):
    return Dict(self._items).set_pos(self.pos_start, self.pos_end).set_context(self.context)
  
  def __len__(self):
    return len(self._items)
  
  def __iter__(self):
    return iter(self._items)
  
  def keys(self):
    return self._items.keys()
    
  def values(self):
    return self._items.values()
    
  def items(self):
    return self._items.items()
    
  def get(self, key, default=None):
    return self.items.get(key, default)
  
  def __len__(self):
    return len(self._items)
    
  def __contains__(self, key):
    return self._items.__contains__(key)
    
  def __getitem__(self, key):
    try:
      return self.get_object().__getitem__(key)
    except TypeError:
      raise errors.TypeError(
        key.pos_start, key.pos_end,
        f"unhashable type: '{key.name}'", self.context, 
      )
    except KeyError as e:
      raise errors.KeyError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )


class Slice(Value):
  name = 'slice'
  def __init__(self, start, stop, step):
    super().__init__()
    if start is None:
      start = null
    if stop is None:
      stop = null
    if step is None:
      step = null
    self.start = start 
    self.stop = stop 
    self.step = step
  
  def get_object(self):
    return slice(self.start.get_object(), self.stop.get_object(), self.step.get_object())
    
  def get_pyobject(self):
    return {k.get_pyobject(): v.get_pyobject() for k, v in self.items()}
  
  def copy(self):
    return Slice(self.start, self.stop, self.step).set_pos(self.pos_start, self.pos_end).set_context(self.context)


class Builtin_Function_Or_Method(Value):
  name = 'builtin_function_or_method'
  def __init__(self, func, _name):
    self.func = func 
    self._name = _name
    
  def get_object(self):
    return self.func
  
  def __repr__(self):
    return f'<built-in function {self._name}>'
  
  def __str__(self):
    return self.__repr__()
  
  def __call__(self, *args, **kwargs):
    return self.func(*args, **kwargs)
  
  def copy():
    pass
