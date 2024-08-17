from abc import abstractmethod
import math, inspect

from ..constants import *
from .. import errors
from .context import Context


def get_attr(object, attr):
  if not isinstance(object, (
    Object, Object._CAT__class__
  )):
    return None
  if 'CAT__getattribute__' in object.__class__.__dict__:
    res = object.CAT__getattribute__(attr_name)
  attr = 'CAT' + attr
  if attr in object.__dict__:
    res = object.__dict__[attr]
  elif attr in object.__class__.__dict__:
    res = object.__class__.__dict__[attr]
  else:
    if 'CAT__getattr__' in object.__class__.__dict__:
      res = object.CAT__getattr__(attr)
    else:
      res = None
  
  if res and get_attr(res, '__get__'):
    return res.CAT__get__(object, object.__class__)
  return res 
    

class Object:
  def __init__(self):
    self.set_pos()
    self.set_context()
  
  class _CAT__class__:
    CAT__name__ = '<anonymous>'
    def CAT__get__(self, instance, type=None):
      return cat_object
  CAT__class__ = _CAT__class__()
  
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
    assert isinstance(other, Object), "binary_op"
    
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
      raise errors.TypeError(
        self.pos_start, self.pos_end, 
        f"'{OP_REDICT[op]}' not supported between instances of '{self.CAT__class__.CAT__name__}' and '{other.CAT__class__.CAT__name__}'", 
        self.context
      )
    return self.invalid(op, other)
  
  def CAT__repr__(self):
    t = super().__repr__()
    return "<object " + t[t.find('object'):]
    
  def CAT__str__(self):
    return self.CAT__repr__()
  
  def __repr__(self):
    return self.CAT__repr__()
    
  def __str__(self):
    return self.CAT__str__()
    
  def __iter__(self):
    return self.CAT__iter__()
    
  def __contains__(self):
    return self.CAT__contains__()
    
  def __getitem__(self):
    return self.CAT__getitem__()
  
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


class cat_property(Object):
  def __init__(self, fget=None, fset=None):
    self.fget = fget
    self.fset = fset

  def CAT__get__(self, obj, type=None):
    if self.fget is None:
      raise AttributeError("unreadable attribute")
    return self.fget(obj)

  def CAT__set__(self, obj, value):
    if self.fset is None:
      raise AttributeError("can't set attribute")
    self.fset(obj, value)

  def getter(self, fget):
    return type(self)(fget, self.fset)

  def setter(self, fset):
    return type(self)(self.fget, fset)


class Type(Object):
  CAT__name__: str = 'type'
  CAT__qualname__: str = 'type'
  def get_object(self):
    return type
      
  @cat_property
  def CAT__dict__(self):
    class mappingproxy(Dict):
      CAT__class__ = mappingproxy_type()
      def __init__(self, value):
        super().__init__(value)
        
      def CATkeys(self):
        return self.value.keys()
    
    return mappingproxy({k[3:]: v for k, v in self.__class__.__dict__.items() if k.startswith('CAT')})
  
  @cat_property
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
      return get_attr(args[0], '__class__')
    return self.CAT__new__(*args, **kwds)
  
  def CAT__new__(self, name, bases, dict, **kwds):
    self.test_type(name, String)
    self.test_type(bases, Tuple)
    self.test_type(dict, Dict)
    a = Type()
    a.CAT__name__ = name.get_object()
    return a
  
cat_type = Type()


class mappingproxy_type(Type):
  CAT__name__ = 'mappingproxy'
  CAT__class__ = cat_type
      

class Property_Type(Type):
  CAT__name__ = 'property'
  CAT__class__ = cat_type

cat_property.CAT__class__ = Property_Type()

    
    
class ObjectType(Type):
  CAT__name__ = 'object'
  CAT__class__ = cat_type
  def CAT__call__(self):
    return Object()

cat_object = ObjectType()


class Single(Object):
  def __init__(self, value):
    super().__init__()
    self.value = value
  
  def get_object(self):
    return self.value
  
  def CAT__repr__(self):
    return repr(self.value)
  
  def CAT__bool__(self):
    return bool(self.value)


class NullType(Type):
  CAT__name__ = 'nulltype'
  CAT__class__ = cat_type
  def CAT__call__(self):
    return null


class Null(Single):
  CAT__class__ = NullType()
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


class BoolType(Type):
  CAT__name__ = 'bool'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return Bool(value.CAT__bool__())


class Bool(Number):
  CAT__class__ = BoolType()
  def __init__(self, value):
    super().__init__(bool(value))


true = Bool(True)
false = Bool(False)


class IntType(Type):
  CAT__name__ = 'int'
  CAT__class__ = cat_type
  def CAT__call__(self, value=0, /, base=Int(10)):
    return Int(int(value.get_object(), base.get_object()))


class Int(Number):
  CAT__class__ = IntType()
  def __init__(self, value):
    super().__init__(int(value))


class FloatType(Type):
  CAT__name__ = 'float'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return Float(value)


class Float(Number):
  CAT__class__ = FloatType()
  def __init__(self, value):
    super().__init__(float(value))


class StringType(Type):
  CAT__name__ = 'str'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return String(value)


class String(Single):
  CAT__class__ = StringType()
  def __init__(self, value):
    super().__init__(str(value))
    
  def __hash__(self):
    return hash(self.value)
    
  def CAT__bool__(self):
    return bool(self.get_object())
    
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


class TupleType(Type):
  CAT__name__ = 'tuple'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return Tuple(value)


class Tuple(Single):
  CAT__class__ = TupleType()
  def __init__(self, value):
    super().__init__(tuple(value))
    
  def get_pyobject(self):
    return tuple(i.get_object() for i in self.value)
    
  def CAT__len__(self):
    return len(self.value)
  
  def CAT__iter__(self):
    return iter(self.value)
  
  def CAT__bool__(self):
    return bool(self.get_object())


class ListType(Type):
  CAT__name__ = 'list'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return List(value)


class List(Single):
  CAT__class__ = ListType()
  def __init__(self, value):
    super().__init__(list(value))
    
  def get_pyobject(self):
    return [i.get_object() for i in self.items]
    
  def CAT__len__(self):
    return len(self.value)
    
  def CAT__iter__(self):
    return iter(self.value)
  
  def CAT__getitem__(self, key):
    if not isinstance(key, (Int, Slice)):
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
      
  def CAT__bool__(self):
    return bool(self.get_object())


class DictType(Type):
  CAT__name__ = 'dict'
  CAT__class__ = cat_type
  def CAT__call__(self, value):
    return Dict(value)


class Dict(Single):
  CAT__class__ = DictType()
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
      
  def get(self, key):
    return self.CATget(key)
 
  def keys(self):
    return self.CATkeys()
    
  def values(self):
    return self.CATvalues()
    
  def items(self):
    return self.CATitems()


class Slice(Object):
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


class Builtin_Function_Or_Method_Type(Type):
  CAT__name__ = 'builtin_function_or_method'
  def CAT__call__(self):
    raise errors.TypeError(
      self.pos_start, self.pos_end,
      "cannot create 'builtin_function_or_method' instances", self.context
    )


class Builtin_Function_Or_Method(Object):
  CAT__class__ = Builtin_Function_Or_Method_Type()
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


class FunctionType(Type):
  CAT__name__ = 'function'
  CAT__class__ = cat_type


class Function(Object):
  CAT__class__ = FunctionType()
  def __init__(self, func):
    super().__init__()
    self.CAT__call__ = func
  
