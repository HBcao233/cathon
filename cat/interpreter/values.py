import math, inspect
from abc import abstractmethod
from ..constants import *
from .. import errors
from .context import Context


class Value:
  @property
  def CAT__class__(self):
    return value_meta
    
  @property
  def CAT__dict__(self):
    return {k: v for k, v in self.__dict__.items() if k.startswith('ATTR')}
  
  def __init__(self):
    self.set_pos()
    self.set_context()
  
  @abstractmethod
  def get_object(self):
    raise NotImplementedError
  
  def get_pyobject(self):
    return self.get_object()
    
  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self
    
  def set_context(self, context: Context = None):
    self.context = context
    return self
    
  def invalid(self, op, other=None, details=None):
    if details is None:
      details = f"invalid {'unary' if other is None else 'binary'} operation: {OP_REDICT[op]}"
    raise errors.OpertionError(
      self.pos_start, self.pos_end,
      details, self.context, 
    )
    
  def unary_op(self, op):
    try:
      if op == PLUS:
        return self.CAT__pos__()
      if op == MINUS:
        return self.CAT__neg__()
      if op == TILDE:
        return self.CAT__invert__()
      if op == EXCLAMATION:
        return not self.CAT__bool__()
    except AttributeError:
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"bad operand type for unary {OP_REDICT[op]}: '{self.CAT__name__}' ",
        context
      )
    return self.invalid(op)
  
  def binary_op(self, op, other):
    assert isinstance(other, Value), "binary_op"
    
    try:
      if op == DOUBLESTAR:
        return self.CAT__pow__(other)
      if op == STAR:
        return self.CAT__mul__(other)
      if op == SLASH:
        return self.CAT__truediv__(other)
      if op == DOUBLESLASH:
        return self.CAT__floordiv__(other)
      if op == PERCENT:
        return self.CAT__mod__(other)
      if op == PLUS:
        return self.CAT__add__(other)
      if op == MINUS:
        return self.CAT__sub__(other)
      if op == DOUBLEAMPER:
        return self.CAT__and__(other)
      if op == DOUBLEVBAR:
        return self or other
      if op == AMPER:
        return self and other
      if op == VBAR:
        return self.CAT__or__(other)
      if op == CIRCUMFLEX:
        return self.CAT__xor__(other)
      if op == LEFTSHIFT:
        return self.CAT__lshift__(other)
      if op == RIGHTSHIFT:
        return self.CAT__rshift__(other)
      if op == EQEQUAL:
        return self.CAT__eq__(other)
      if op == NOTEQUAL:
        return not self.CAT__eq__(other)
      if op == AT:
        return self.CAT__AT__(other)
        
      try:
        if op == LESS:
          return self.CAT__lt__(other)
        if op == GREATER:
          return not self.CAT__le__(other)
        if op == LESSEQUAL:
          return self.CAT__le__(other)
        if op == GREATEREQUAL:
          return not self.CAT__lt__(other)
      except AttributeError:
        if op == LESS:
          return not self.CAT__ge__(other)
        if op == GREATER:
          return self.CAT__gt__(other)
        if op == LESSEQUAL:
          return not self.CAT__gt__(other)
        if op == GREATEREQUAL:
          return self.CAT__ge__(other)
      
    except AttributeError:
      return errors.TypeError(
        self.pos_start, self.pos_end, 
        f"'{OP_REDICT[op]}' not supported between instances of '{self.CAT__name__}' and '{other.CAT__name__}'", 
        self.context
      )
    return self.invalid(op, other)
  
  def CAT__repr__(self):
    return f"<class '{self.CAT__class__.CAT__name__}'>"
    
  def CAT__str__(self):
    return self.CAT__repr__()
  
  def __repr__(self):
    return self.CAT__repr__()
    
  def __str__(self):
    return self.CAT__str__()
  
  def __len__(self):
    return self.CAT__len__()
    
  def __iter__(self):
    return self.CAT__iter__()
    
  def __contains__(self):
    return self.CAT__contains__()
    
  def __getitem__(self):
    return self.CAT__getitem__()
  
  def get(self, key):
    return self.CATget(key)
 
  def keys(self):
    return self.CATkeys()
    
  def values(self):
    return self.CATvalues()
    
  def items(self):
    return self.CATitems()
  
  def test_type(self, obj, expected_type):
    func_name = inspect.stack(1)[1].function[3:]
    if func_name == '__call__':
      func_name = ''
    func_name = self.CAT__name__ + func_name
    if not isinstance(obj, expected_type):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f'{func_name}() argument 1 must be {expected_type.CAT__class__.CAT__name__}, not {obj.CAT__class__.CAT__name__}',
        self.context,
      )
    

class Meta(Value):
  CAT__name__: str = 'type'
  CAT__qualname__: str = 'type'
  
  def get_object(self):
    return type
    
  @property
  def CAT__class__(self):
    return self
    
  def CAT__repr__(self):
    return f"<class '{self.CAT__name__}'>"
    
  def CAT__call__(self, *args, **kwds):
    """
    type(object) -> the object's type
    type(name, bases, dict, **kwds) -> a new type
    """
    if len(args) not in (1,3):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        'type() takes 1 or 3 arguments',
        self.context,
      )
    if len(args) == 1:
      return args[0].CAT__class__
    return self.CAT__new__(*args, **kwds)
  
  def CAT__new__(self, name, bases, dict, **kwds):
    self.test_type(name, String)
    self.test_type(bases, Tuple)
    self.test_type(dict, Dict)
    a = Meta()
    a.CAT__name__ = name.get_object()
    return a
  
meta = Meta()


class ValueMeta(Meta):
  CAT__name__ = 'object'
  CAT__class__ = meta

value_meta = ValueMeta()


class Single(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value
  
  def get_object(self):
    return self.value
  
  def CAT__repr__(self):
    return repr(self.value)


class Number(Single):
  def __init__(self, value):
    super().__init__(value)
      
  def zero_error(self):
    raise errors.OpertionError(
      self.pos_start, self.pos_end,
      'division by zero', self.context, 
    )
    
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
    
  def CAT__repr__(self):
    if self.CAT__class__.CAT__name__ == 'bool':
      return self.bool_to_string()
    if self.CAT__class__.CAT__name__ == 'float':
      if self.get_object() == float('-inf'):
        return '-Inf'
      if self.get_object() == float('inf'):
        return 'Inf'
      if math.isnan(self.get_object()):
        return 'NaN'
    return str(self.value)
    
  def CAT__abs__(self):
    return abs(self.value)
    
  def CAT__pos__(self):
    return +(self.get_object())
    
  def CAT__neg__(self):
    return -(self.get_object())
    
  def CAT__invert__(self):
    return ~(self.get_object())
  
  def CAT__pow__(self, other):
    return self.get_object() ** other.get_object()
    
  def CAT__add__(self, other):
    return self.get_object() + other.get_object()
  
  def CAT__sub__(self, other):
    return self.get_object() - other.get_object()
    
  def CAT__mul__(self, other):
    return self.get_object() * other.get_object()
    
  def CAT__truediv__(self, other):
    return self.get_object() / other.get_object()
  
  def CAT__floordiv__(self, other):
    return self.get_object() // other.get_object()
  
  def CAT__mod__(self, other):
    return self.get_object() % other.get_object()
    
  def CAT__and__(self, other):
    return self.get_object() & other.get_object()
  
  def CAT__or__(self, other):
    return self.get_object() | other.get_object()
  
  def CAT__xor__(self, other):
    return self.get_object() ^ other.get_object()
  
  def CAT__lshift__(self, other):
    return self.get_object() << other.get_object()
    
  def CAT__rshift__(self, other):
    return self.get_object() >> other.get_object()
  
  def CAT__bool__(self):
    return bool(self.get_object())
    
  def CAT__hash__(self):
    return hash(self.get_object())

  def CAT__eq__(self, other):
    return self.get_object() == other.get_object()
    
  def CAT__lt__(self, other):
    return self.get_object() < other.get_object()
    
  def CAT__ne__(self, other):
    return not self.CAT__eq__(other)
    
  def CAT__le__(self, other):
    return self.__lt__(other) or self.__eq__(other)


class BoolMeta(ValueMeta):
  CAT__name__ = 'bool'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return Bool(value)
  

class IntMeta(ValueMeta):
  CAT__name__ = 'int'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return Int(value)


class FloatMeta(ValueMeta):
  CAT__name__ = 'float'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return Float(value)

bool_meta = BoolMeta()
int_meta = IntMeta()
float_meta = FloatMeta()
class Bool(Number):
  CAT__class__ = bool_meta
  def __init__(self, value):
    super().__init__(bool(value))


class Int(Number):
  CAT__class__ = int_meta
  def __init__(self, value):
    super().__init__(int(value))


class Float(Number):
  CAT__class__ = float_meta
  def __init__(self, value):
    super().__init__(float(value))
    
true = Bool(True)
false = Bool(False)


class StringMeta(ValueMeta):
  CAT__name__ = 'str'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return str(value)
    
string_meta = StringMeta()

class String(Single):
  CAT__class__ = string_meta
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


class NullMeta(ValueMeta):
  CAT__name__ = 'nulltype'
  CAT__class__ = value_meta
  def CAT__call__(self):
    return null

nulltype = NullMeta()

class Null(Single):
  CAT__class__ = nulltype
  def __init__(self):
    super().__init__(None)
  
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

null = Null()


class TupleMeta(ValueMeta):
  CAT__name__ = 'tuple'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return Tuple(value)
tuple_meta = TupleMeta()

class Tuple(Single):
  CAT__class__ = tuple_meta
  def __init__(self, value):
    super().__init__(tuple(value))
    
  def get_pyobject(self):
    return tuple(i.get_object() for i in self.value)
    
  def CAT__len__(self):
    return len(self.value)
  
  def CAT__iter__(self):
    return iter(self.value)
  
  
  
class ListMeta(ValueMeta):
  CAT__name__ = 'list'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return List(value)


class List(Single):
  CAT__class__ = ListMeta
  def __init__(self, value):
    super().__init__(list(value))
    
  def get_pyobject(self):
    return [i.get_object() for i in self.items]
    
  def CAT__len__(self):
    return len(self.value)
    
  def CAT__iter__(self):
    return iter(self.value)
  
  def CAT__getitem__(self, key):
    if key.name not in ('int', 'slice'):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"list indices must be integers or slices, not {key.name}", self.context, 
      )
    try:
      return self.value.__getitem__(key.get_object())
    except IndexError as e:
      raise errors.IndexError(
        key.pos_start, key.pos_end,
        str(e), self.context,
      )
      
  def CAT__setitem__(self, key, value):
    if key.name not in ('int', 'slice'):
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"string indices must be integers or slices, not {key.name}", self.context, 
      )
    
    try:
      return self.value.__setitem__(key.get_object(), value)
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


class DictMeta(ValueMeta):
  CAT__name__ = 'dict'
  CAT__class__ = value_meta
  def CAT__call__(self, value):
    return Dict(value)
dict_meta = DictMeta

class Dict(Single):
  CAT__class__ = dict_meta
  def __init__(self, value: dict):
    super().__init__(value)

  def get_pyobject(self):
    return {k.get_object(): v.get_object() for k, v in self.value.items()}
  
  def CAT__len__(self):
    return len(self.value)
    
  def CAT__iter__(self):
    return iter(self.value)
  
  def CATkeys(self):
    return self.value.keys()
    
  def CATvalues(self):
    return self.value.values()
    
  def CATitems(self):
    return self.value.items()
    
  def CATget(self, key, default=None):
    return self.value.get(key, default)
    
  def CAT__contains__(self, key):
    return self.value.__contains__(key)
    
  def CAT__getitem__(self, key):
    try:
      return self.value.__getitem__(key)
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


class Builtin_Function_Or_Method_Meta(Meta):
  CAT__name__ = 'builtin_function_or_method'
  def CAT__call__(self):
    raise errors.TypeError(
      self.pos_start, self.pos_end,
      "cannot create 'builtin_function_or_method' instances", self.context
    )

builtin_function_or_method_meta = Builtin_Function_Or_Method_Meta()

class Builtin_Function_Or_Method(Value):
  CAT__class__ = builtin_function_or_method_meta
  def __init__(self, func):
    self.func = func 
    self.CAT__name__ = func.__name__
    
  def get_object(self):
    return self.func
  
  def CAT__repr__(self):
    return f'<built-in function {self.CAT__name__}>'
  
  def CAT__str__(self):
    return self.__repr__()
  
  def CAT__call__(self, *args, **kwargs):
    try:
      return self.func(*args, **kwargs)
    except errors.AttributeError:
      raise errors.TypeError(
        self.pos_start, self.pos_end,
        f"bad operand type for {name.replace('_', '')}(): '{self.CAT__name__}'", self.context
      )
