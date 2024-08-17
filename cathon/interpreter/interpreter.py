from itertools import chain
from .. import errors
from ..parser.nodes import *
from .values import *


def auto(val) -> Object:
  if isinstance(val, Object):
    return val
  if isinstance(val, bool):
    return Bool(val)
  if isinstance(val, int):
    return Int(val)
  if isinstance(val, float):
    return Float(val)
  if val is None:
    return null
  if isinstance(val, str):
    return String(val)
  if isinstance(val, tuple):
    return Tuple(val)
  if isinstance(val, list):
    return List(val)
  if callable(val):
    return Function(val)
  return Single(val)
  
  
class Interpreter(object):
  @classmethod
  def visit(cls, node, context):
    method_name = f'visit_{type(node).__name__}'
    if not hasattr(cls, method_name):
      raise AttributeError(f'No visit method "{method_name}"')
    return getattr(cls, method_name)(node, context)
  
  @staticmethod
  def visit_NumberNode(node, context):
    return auto(node.value.value).set_pos(node.value.pos_start, node.value.pos_end).set_context(context)
    
  @staticmethod
  def visit_StringNode(node, context):
    return String(node.value.value).set_pos(node.value.pos_start, node.value.pos_end).set_context(context)
  
  @classmethod
  def visit_UnaryOpNode(cls, node, context):
    num = cls.visit(node.right, context)
    val = num.unary_op(node.op.type)
    return auto(val).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_BinaryOpNode(cls, node, context):
    left = cls.visit(node.left, context)
    right = cls.visit(node.right, context)
    try:
      val = left.binary_op(node.op.type, right)
    except errors.BaseError as e:
      try:
        val = right.binary_op(node.op.type, left)
      except errors.BaseError:
        raise e
    return auto(val).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @staticmethod
  def visit_VarAccessNode(node, context):
    var_name = node.var.value
    value = context.symbol_table.get(var_name)
    if value is context.symbol_table.undefined:
      raise errors.NameError(
        node.pos_start, node.pos_end,
        f"name '{var_name}' is not defined", context
      )
    return auto(value).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_VarAssignNode(cls, node, context):
    var_name = node.var.value
    value = cls.visit(node.value, context)
    value = auto(value)
    context.symbol_table.set(var_name, value)
    return value.set_pos(node.pos_start, node.pos_end).set_context(context)
    
  @staticmethod
  def visit_VarDeleteNode(node, context):
    if not isinstance(node.var, list):
      node.var = [node.var]
    for i in node.var:
      res = context.symbol_table.remove(i.value)
      if res is context.symbol_table.undefined:
        raise errors.NameError(
          i.pos_start, i.pos_end,
          f"name '{i.value}' is not defined", context
        )
  
  @classmethod
  def visit_TupleNode(cls, node, context):
    elements = (auto(cls.visit(i, context)) for i in node.items)
    return Tuple(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_ListNode(cls, node, context):
    elements = (auto(cls.visit(i, context)) for i in node.items)
    return List(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_DictNode(cls, node, context):
    elements = {}
    for k, v in node.items.items():
      key = auto(cls.visit(k, context))
      try:
        elements[key] = auto(cls.visit(v, context))
      except TypeError:
        raise errors.TypeError(
          key.pos_start, key.pos_end,
          f'unhashable type: {key.name}', context
        )
    return Dict(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_SliceNode(cls, node, context):
    start = stop = step = None
    if node.start is not None: 
      start = cls.visit(node.start, context)
    if node.stop is not None: 
      stop = cls.visit(node.stop, context)
    if node.step is not None: 
      step = cls.visit(node.step, context)
    return Slice(start, stop, step).set_pos(node.pos_start, node.pos_end).set_context(context)
  
  
  @classmethod
  def visit_GetAttrNode(cls, node, context):
    object = cls.visit(node.object, context)
    attr_name = node.attr_name.value
    
    res = cat_getattr(object, attr_name)
    if res is None:
      raise errors.AttributeError(
        node.pos_start, node.pos_end,
        f"'{object.CAT__class__.CAT__name__}' object has no attribute '{attr_name}'", context
      )
      
    return auto(res).set_pos(node.pos_start, node.pos_end).set_context(context)
    
  @classmethod
  def visit_SetAttrNode(cls, node, context):
    object = cls.visit(node.object, context)
    attr_name = node.attr_name.value
    value = auto(cls.visit(node.value, context))
    auto(object.CAT__setattribute__(attr_name, value))
    return value.set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_GetItemNode(cls, node, context):
    object = cls.visit(node.object, context)
    if not hasattr(object, 'CAT__getitem__'):
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.CAT__class__.CAT__name__}' object is not subscriptable", context
      )
    key = cls.visit(node.key, context)
    res = auto(object.CAT__getitem__(key))
    return res.set_pos(node.pos_start, node.pos_end).set_context(context)
    
  @classmethod
  def visit_SetItemNode(cls, node, context):
    object = cls.visit(node.object, context)
    if not hasattr(object, 'CAT__setitem__'):
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.name}' object does not support item assignment", context
      )
    key = cls.visit(node.key, context)
    value = auto(cls.visit(node.value, context))
    object.CAT__setitem__(key, value)
    return value.set_pos(node.pos_start, node.pos_end).set_context(context)
  
  @classmethod
  def visit_IfNode(cls, node, context):
    oneline = node.oneline
    for condition, body in node.cases:
      condition_value = cls.visit(condition, context)
      if bool(condition_value):
        res = cls.visit(body, context)
        if oneline: 
          return auto(res).set_pos(body.pos_start, body.pos_end).set_context(context)
    
    if node.else_block:
      res = cls.visit(node.else_block, context)
      if oneline:
        return auto(res).set_pos(node.else_block.pos_start, node.else_block.pos_end).set_context(context)
        
  @classmethod
  def visit_CallNode(cls, node, context):
    object = cls.visit(node.object, context)
    if 'CAT__call__' not in object.__dict__ and 'CAT__call__' not in object.__class__.__dict__:
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.CAT__class__.CAT__name__}' object is not callable", context
      )
    args = cls.visit(node.args, context)
    if isinstance(object, Function) and isinstance(node.object, GetAttrNode):
      args = Tuple((cls.visit(node.object.object, context), *args))
    kwargs = cls.visit(node.kwargs, context)
    try:
      res = object.CAT__call__(*args, **kwargs)
    except errors.RuntimeError:
      raise
    except TypeError as e:
      if 'CAT__name__' in object.__dict__:
        name = object.CAT__name__
      else:
        name = object.CAT__class__.CAT__name__
      raise errors.TypeError(
        node.pos_start, node.pos_end,
        f"{name}() "+ str(e)[str(e).find('() ')+3:],
        context,
      )
    except Exception as e:
      raise errors.RuntimeError(
        node.pos_start, node.pos_end,
        str(e), context, e.__class__.__name__
      )
    return auto(res).set_pos(node.pos_start, node.pos_end).set_context(context)
  