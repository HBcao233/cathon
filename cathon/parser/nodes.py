from abc import abstractmethod
from collections.abc import Sequence, Mapping
from typing import Union
from ..lexer.position import Position
from ..lexer.tokens import Token


class ASTNode(object):
  pos_start: Position
  pos_end: Position

  @abstractmethod
  def __repr__(self):
    pass


class ProgramNode(ASTNode):
  def __init__(
    self,
    body: list[ASTNode],
    pos_start,
    pos_end,
  ):
    self.body = body
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'ProgramNode(body={self.body})'


class SingleNode(ASTNode):
  """
  单值节点
  """

  type = 'single'

  def __init__(self, value: Token):
    self.value = value

    self.pos_start = value.pos_start.copy()
    self.pos_end = value.pos_end.copy()

  def __repr__(self):
    return f'SingleNode(type={self.type}, value={self.value})'


class CommentNode(SingleNode):
  type = 'comment'


class NumberNode(SingleNode):
  type = 'number'


class StringNode(SingleNode):
  type = 'string'


class UnaryOpNode(ASTNode):
  """
  一元运算符节点
  """

  def __init__(
    self,
    op: Token,
    right: ASTNode,
  ):
    self.op = op
    self.right = right

    self.pos_start = op.pos_start.copy()
    self.pos_end = right.pos_end.copy()

  def __repr__(self):
    return f'UnaryOpNode(op={self.op}, right={self.right})'


class BinaryOpNode(ASTNode):
  """
  二元运算符节点
  """

  def __init__(self, left: Token, op: Token, right: Token):
    self.left = left
    self.op = op
    self.right = right

    self.pos_start = left.pos_start.copy()
    self.pos_end = right.pos_end.copy()

  def __repr__(self):
    return f'BinaryOpNode(left={self.left}, op={self.op}, node={self.right})'


class VarAccessNode(ASTNode):
  """
  变量访问节点
  """

  def __init__(self, var: Token):
    self.var = var

    self.pos_start = var.pos_start.copy()
    self.pos_end = var.pos_end.copy()

  def __repr__(self):
    return f'VarAccessNode(var={self.var})'


class VarAssignNode(ASTNode):
  """
  变量设置节点
  """

  def __init__(
    self,
    var: Union[Token, VarAccessNode],
    value: ASTNode,
  ):
    if isinstance(var, VarAccessNode):
      var = var.var
    self.var = var
    self.value = value

    self.pos_start = var.pos_start.copy()
    self.pos_end = value.pos_end.copy()

  def __repr__(self):
    return f'VarAssignNode(var={self.var}, value={self.value})'


class VarDeleteNode(ASTNode):
  """
  变量删除节点
  """

  def __init__(self, var: Token, pos_start, pos_end):
    self.var = var

    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'DeleteNode(targets={self.var})'


class TupleNode(ASTNode):
  """
  元组节点
  """

  def __init__(self, items: Sequence[ASTNode], pos_start, pos_end):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'TupleNode(items={self.items})'


class ListNode(ASTNode):
  """
  列表节点
  """

  def __init__(self, items: Sequence[ASTNode], pos_start, pos_end):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'ListNode(items={self.items})'


class SliceNode(ASTNode):
  """
  切片节点
  """

  def __init__(
    self,
    start: ASTNode,
    stop: ASTNode,
    step: ASTNode,
    pos_start,
    pos_end,
  ):
    self.start = start
    self.stop = stop
    self.step = step
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    start = stop = step = None
    if start is not None:
      start = self.start.__repr__()
    if stop is not None:
      stop = self.stop.__repr__()
    if step is not None:
      step = self.step.__repr__()
    return f'SliceNode(items={self.items})'


class GetItemNode(ASTNode):
  """
  索引值访问节点
  """

  def __init__(self, object: ASTNode, key: ASTNode, pos_start, pos_end):
    self.object = object
    self.key = key
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'GetItemNode(value={self.items}, slice={self.key})'


class SetItemNode(ASTNode):
  """
  索引值设置节点
  """

  def __init__(
    self,
    object: ASTNode,
    key: ASTNode,
    value: ASTNode,
    pos_start: Position,
  ):
    self.object = object
    self.key = key
    self.value = value

    self.pos_start = pos_start
    self.pos_end = value.pos_end.copy()

  def __repr__(self):
    return f'AssignNode(targets={self.var}, {self.key}, value={self.value})'


class GetAttrNode(ASTNode):
  """
  属性值访问节点
  """

  def __init__(self, object: ASTNode, attr_name: Token, pos_start, pos_end):
    self.object = object
    self.attr_name = attr_name

    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'GetAttrNode(value={self.object}, attr={self.attr_name})'


class SetAttrNode(ASTNode):
  """
  属性值设置节点
  """

  def __init__(self, object: ASTNode, attr_name: Token, value: ASTNode, pos_start):
    self.object = object
    self.attr_name = attr_name
    self.value = value
    self.pos_start = pos_start
    self.pos_end = value.pos_end.copy()

  def __repr__(self):
    return f'AssignNode(targets={self.object}, {self.attr_name}, value={self.value})'


class DictNode(ASTNode):
  def __init__(self, items: Mapping[ASTNode, ASTNode], pos_start, pos_end):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'DictNode(items={self.items})'


class IfNode(ASTNode):
  def __init__(
    self,
    test: ASTNode,
    body: Sequence[ASTNode],
    orelse: ASTNode,
    pos_start,
    pos_end,
  ):
    self.test = test
    self.body = body
    self.orelse = orelse

    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'IfNode(test={self.test}, body={self.body}, orelse={self.orelse})'


class IfExprNode(ASTNode):
  def __init__(
    self,
    test: ASTNode,
    body: Sequence[ASTNode],
    orelse: ASTNode = None,
  ):
    self.test = test
    self.body = body
    self.orelse = orelse

    self.pos_start = body.pos_start
    self.pos_end = orelse.pos_end

  def __repr__(self):
    return f'IfExprNode(test={self.test}, body={self.body}, orelse={self.orelse})'


class CallNode(ASTNode):
  def __init__(
    self,
    object: ASTNode,
    args: TupleNode,
    kwargs: DictNode,
    pos_start,
    pos_end,
  ):
    self.object = object
    self.args = args
    self.kwargs = kwargs

    self.pos_start = pos_start
    self.pos_end = pos_end

  def __repr__(self):
    return f'CallNode(func={self.object}, args={self.args}, kwargs={self.kwargs})'
