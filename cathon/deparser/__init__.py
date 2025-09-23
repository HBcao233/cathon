from ..parser.nodes import *


class Deparser:
  class Context(object):
    def __init__(self, indent=0):
      self.indent = indent

    def __str__(self):
      return '  ' * self.indent

    def __repr__(self):
      return f'Context(indent={self.indent})'

    def add_indent(self, count=1):
      return Deparser.Context(self.indent + count)

  @classmethod
  def visit(cls, node, context):
    method_name = f'visit_{type(node).__name__}'
    if not hasattr(cls, method_name):
      raise AttributeError(f'No visit method "{method_name}"')
    return getattr(cls, method_name)(node, context)

  @classmethod
  def visit_ProgramNode(cls, node, context):
    body = [cls.visit(i, context) for i in node.body]
    return '\n'.join(body)

  @staticmethod
  def visit_CommentNode(node, context):
    if '\n' not in node.value.value:
      return f'{context}#{node.value.value}'
    return f'{context}"""\n{node.value.value}\n"""'

  @staticmethod
  def visit_NumberNode(node, context):
    return f'{context}{node.value.value}'

  @staticmethod
  def visit_StringNode(node, context):
    return f'{context}{repr(node.value.value)}'

  @classmethod
  def visit_UnaryOpNode(cls, node, context):
    num = cls.visit(node.right, context)
    op = OP_REDICT[node.op.type]
    return f'{context}{op}{num}'

  @classmethod
  def visit_BinaryOpNode(cls, node, context):
    left = cls.visit(node.left, context)
    right = cls.visit(node.right, context)
    op = OP_REDICT[node.op.type]
    return f'{context}{left} {op} {right}'

  @staticmethod
  def visit_VarAccessNode(node, context):
    var_name = node.var.value
    return f'{context}{var_name}'

  @classmethod
  def visit_VarAssignNode(cls, node, context):
    var_name = node.var.value
    value = cls.visit(node.value, context)
    return f'{context}{var_name} = {value}'

  @staticmethod
  def visit_VarDeleteNode(node, context):
    if not isinstance(node.var, list):
      node.var = [node.var]
    var_names = ', '.join(i.value for i in node.var)
    return f'{context}del {var_names}'

  @classmethod
  def visit_TupleNode(cls, node, context):
    elements = ', '.join(cls.visit(i, context) for i in node.items)
    return f'({elements})'

  @classmethod
  def visit_ListNode(cls, node, context):
    elements = ', '.join(cls.visit(i, context) for i in node.items)
    return f'[{elements}]'

  @classmethod
  def visit_DictNode(cls, node, context):
    elements = ', '.join([f'{k}: {v}' for k, v in node.items.items()])
    return '{' + elements + '}'

  @classmethod
  def visit_SliceNode(cls, node, context):
    start = stop = step = None
    if node.start is not None:
      start = cls.visit(node.start, context)
    if node.stop is not None:
      stop = cls.visit(node.stop, context)
    if node.step is not None:
      step = cls.visit(node.step, context)
    return f'{start}:{stop}:{step}'

  @classmethod
  def visit_GetAttrNode(cls, node, context):
    object = cls.visit(node.object, context)
    attr_name = node.attr_name.value

    res = cat_getattr(object, attr_name)
    if res is None:
      raise errors.AttributeError(
        node.pos_start,
        node.pos_end,
        f"'{object.CAT__class__.CAT__name__}' object has no attribute '{attr_name}'",
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
        node.pos_start,
        node.pos_end,
        f"'{object.CAT__class__.CAT__name__}' object is not subscriptable",
      )
    key = cls.visit(node.key, context)
    res = auto(object.CAT__getitem__(key))
    return res.set_pos(node.pos_start, node.pos_end).set_context(context)

  @classmethod
  def visit_SetItemNode(cls, node, context):
    object = cls.visit(node.object, context)
    if not hasattr(object, 'CAT__setitem__'):
      raise errors.TypeError(
        node.pos_start,
        node.pos_end,
        f"'{object.name}' object does not support item assignment",
      )
    key = cls.visit(node.key, context)
    value = auto(cls.visit(node.value, context))
    object.CAT__setitem__(key, value)
    return value.set_pos(node.pos_start, node.pos_end).set_context(context)

  @classmethod
  def visit_IfNode(cls, node, context):
    result = []
    test = cls.visit(node.test, Deparser.Context())
    body = '\n'.join(cls.visit(i, context.add_indent(1)) for i in node.body)
    result.append(f'{context}if {test}:\n{body}\n')
    if node.orelse:
      if len(node.orelse) == 1 and isinstance(node.orelse[0], IfNode):
        orelse = cls.visit(node.orelse[0], context)
        orelse = f'{context}el{orelse}'
      else:
        orelse = '\n'.join(cls.visit(i, context.add_indent(1)) for i in node.orelse)
        orelse = f'{context}else:\n{orelse}\n'

      result.append(orelse)
    return ''.join(result)

  @classmethod
  def visit_CallNode(cls, node, context):
    _object = cls.visit(node.object, Deparser.Context())
    args = cls.visit(node.args, Deparser.Context(0))[1:][:-1]
    kwargs = cls.visit(node.kwargs, context)[1:][:-1]
    if kwargs:
      kwargs = ', ' + kwargs
    return f'{context}{_object}({args}{kwargs})'
