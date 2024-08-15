from .values import *
from .. import errors
from ..parser.nodes import *


def auto(val) -> Value:
  if isinstance(val, Value):
    return val
  if isinstance(val, (bool, int, float)):
    return Number(val)
  if val is None:
    return null
  if isinstance(val, str):
    return String(val)
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
    return Number(node.value.value).set_pos(node.value.pos_start, node.value.pos_end).set_context(context)
    
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
  def visit_ListNode(cls, node, context):
    elements = [
      auto(v)
      for i in node.items 
      if i and (v := cls.visit(i, context)) is not None
    ]
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
  def visit_GetItemNode(cls, node, context):
    object = cls.visit(node.object, context)
    if not hasattr(object, '__getitem__'):
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.name}' object is not subscriptable"
      )
    key = cls.visit(node.key, context)
    res = auto(object.__getitem__(key))
    return res.set_pos(node.pos_start, node.pos_end).set_context(context)
    
  @classmethod
  def visit_SetItemNode(cls, node, context):
    object = cls.visit(node.object, context)
    if not hasattr(object, '__setitem__'):
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.name}' object does not support item assignment", context
      )
    key = cls.visit(node.key, context)
    value = auto(cls.visit(node.value, context))
    object.__setitem__(key, value)
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
    if not hasattr(object, '__call__'):
      raise errors.TypeError(
        node.pos_start, node.pos_end, 
        f"'{object.name}' object is not callable", context
      )
    args = cls.visit(node.args, context)
    kwargs = cls.visit(node.kwargs, context)
    kwargs = kwargs.get_pyobject()
    res = object.__call__(*args, **kwargs)
    return auto(res).set_pos(node.pos_start, node.pos_end).set_context(context)
