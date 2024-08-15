from abc import abstractmethod
from collections.abc import Sequence, Mapping
from ..lexer.position import Position
from ..lexer.tokens import Token


class ASTNode(object):
  pos_start: Position
  pos_end: Position
  
  @abstractmethod
  def to_dict(self):
    pass
  
  def __repr__(self):
    return str(self.to_dict())
  
  
class SingleNode(ASTNode):
  """
  单值节点
  """
  type = 'single'
  def __init__(self, value: Token):
    self.value = value
    
    self.pos_start = value.pos_start.copy()
    self.pos_end = value.pos_end.copy()
    
  def to_dict(self):
    return {
      'type': self.type,
      'value': self.value.to_dict()
    }
  
  
class NumberNode(SingleNode):
  type = 'number'
  

class StringNode(SingleNode):
  type = 'string'
    

class UnaryOpNode(ASTNode):
  """
  一元运算符节点
  """
  def __init__(self, op, right):
    self.op = op 
    self.right = right 
    
    self.pos_start = op.pos_start.copy()
    self.pos_end = right.pos_end.copy()
    
  def to_dict(self):
    return {
      'type': 'unary',
      'op': self.op.to_dict(),
      'right': self.right.to_dict(),
    }


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
    
  def to_dict(self):
    return {
      'type': 'binary',
      'left': self.left.to_dict(),
      'op': self.op.to_dict(),
      'right': self.right.to_dict(),
    }


class VarAccessNode(ASTNode):
  """
  变量访问节点
  """
  def __init__(self, var: Token):
    self.var = var
    
    self.pos_start = var.pos_start.copy()
    self.pos_end = var.pos_end.copy()
    
  def to_dict(self):
    return {
      'type': 'var-access',
      'var': self.var.to_dict(),
    }


class VarAssignNode(ASTNode):
  """
  变量设置节点
  """
  def __init__(self, 
    var: Token | VarAccessNode, 
    value: ASTNode,
  ):
    if isinstance(var, VarAccessNode):
      var = var.var
    self.var = var
    self.value = value
    
    self.pos_start = var.pos_start.copy()
    self.pos_end = value.pos_end.copy()
    
  def to_dict(self):
    return {
      'type': 'var-assign',
      'var': self.var.to_dict(),
      'value': self.value.to_dict(),
    }

class VarDeleteNode(ASTNode):
  """
  变量删除节点
  """
  def __init__(
    self, 
    var: Token, 
    pos_start, pos_end
  ):
    self.var = var
    
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'var-delete',
      'var': self.var.to_dict(),
    }


class TupleNode(ASTNode):
  """
  元组节点
  """
  def __init__(
    self, 
    items: Sequence[ASTNode], 
    pos_start, pos_end
  ):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'list',
      'items': [i.to_dict() for i in self.items],
    }


class ListNode(ASTNode):
  """
  列表节点
  """
  def __init__(
    self, 
    items: Sequence[ASTNode], 
    pos_start, pos_end
  ):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'list',
      'items': [i.to_dict() for i in self.items],
    }


class SliceNode(ASTNode):
  """
  切片节点
  """
  def __init__(self, 
    start: ASTNode,
    stop: ASTNode,
    step: ASTNode,
    pos_start, pos_end,
  ):
    self.start = start
    self.stop = stop
    self.step = step
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    start = stop = step = None
    if start is not None:
      start = self.start.to_dict()
    if stop is not None:
      stop = self.stop.to_dict()
    if step is not None:
      step = self.step.to_dict()
    return {
      'type': 'slice',
      'start': start,
      'stop': stop,
      'step': step,
    }


class GetItemNode(ASTNode):
  """
  索引值访问节点
  """
  def __init__(
    self, 
    object: ASTNode, 
    key: ASTNode, 
    pos_start, pos_end
  ):
    self.object = object
    self.key = key
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'get-item',
      'object': self.object.to_dict(),
      'key': self.key.to_dict(),
    }


class SetItemNode(ASTNode):
  """
  索引值设置节点
  """
  def __init__(self, 
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
    
  def to_dict(self):
    return {
      'type': 'var-assign',
      'var': self.var.to_dict(),
      'value': self.value.to_dict(),
    }


class GetAttrNode(ASTNode):
  """
  属性值访问节点
  """
  def __init__(self, object: ASTNode, key: ASTNode, pos_start, pos_end):
    self.object = object
    self.key = key
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'get-attr',
      'object': self.object.to_dict(),
      'key': self.key.to_dict(),
    }


class DictNode(ASTNode):
  def __init__(self, items: Mapping[ASTNode, ASTNode], pos_start, pos_end):
    self.items = items
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return {
      'type': 'dict',
      'items': [(k.to_dict(), v.to_dict()) for k, v in self.items.items()],
    }


class IfNode(ASTNode):
  def __init__(self, 
    oneline: bool,
    cases: Mapping[ASTNode, ASTNode], 
    else_block: ASTNode = None
  ):
    self.oneline = oneline
    self.cases = cases
    self.else_block = else_block
    self.pos_start = cases[0][0].pos_start
    self.pos_end = (else_block or cases[-1][-1]).pos_end
    
  def to_dict(self):
    cases = [{
      'condition': condition.to_dict(),
      'block': block.to_dict(),
    } for condition, block in self.cases]
    else_block = None
    if self.else_block:
      else_block = self.else_block.to_dict()
    return  {
      'type': 'if',
      'oneline': self.oneline,
      'cases': cases,
      'else_block': else_block,
    }

class CallNode(ASTNode):
  def __init__(self, 
    object: ASTNode,
    args: ListNode,
    kwargs: DictNode,
    pos_start, pos_end,
  ):
    self.object = object
    self.args = args
    self.kwargs = kwargs
    self.pos_start = pos_start
    self.pos_end = pos_end
    
  def to_dict(self):
    return  {
      'type': 'call',
      'object': self.object,
      'args': self.args.to_dict(),
      'kwargs': self.kwargs.to_dict(),
    }