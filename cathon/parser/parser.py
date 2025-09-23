from contextlib import contextmanager
from .nodes import *
from ..constants import *
from .. import errors


class Parser(object):
  def __init__(self, tokens):
    self.tokens = tokens
    self.index = -1
    self.token = None
    self.advance()

  def advance(self, count=1):
    self.index += count
    self.update()
    if self.token.type == NL:
      self.advance()
      if self.token.type == NEWLINE:
        self.advance()
    return self.token

  def reverse(self, count=1):
    self.index -= count
    self.update()
    return self.token

  def reverse_to(self, index):
    self.index = index
    self.update()
    return self.token

  def update(self):
    if 0 <= self.index < len(self.tokens):
      self.token = self.tokens[self.index]

  def lookahead(self, count=1):
    index = self.index + count
    if index < len(self.tokens):
      return self.tokens[index]

  @contextmanager
  def try_register(self):
    old_index = self.index
    try:
      yield old_index
    except errors.SyntaxError:
      self.reverse_to(old_index)

  def parse(self):
    return self.program()

  def blanks(self):
    count = 0
    while self.token.type == NEWLINE:
      self.advance()
      count += 1
    return count

  def program(self) -> TupleNode:
    res = self.statements()
    if not ISEOF(self.token.type):
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'the statement must not exist',
      )
    return ProgramNode(res.items, res.pos_start.copy(), res.pos_end.copy())

  def statements(self) -> TupleNode:
    pos_start = self.token.pos_start.copy()
    res = []
    self.blanks()
    if ISEOF(self.token.type):
      return TupleNode(res, pos_start, self.token.pos_end.copy())

    res.extend(self.statement())
    while self.blanks() and not ISEOF(self.token.type) and self.token.type != RBRACE:
      # with self.try_register():
      r = self.statement()
      res.extend(r)
    return TupleNode(res, pos_start, self.token.pos_end.copy())

  def statement(self) -> list[ASTNode]:
    return self.stmts()

  def stmts(self) -> list[ASTNode]:
    items = []
    items.append(self.stmt())
    while self.token.type == SEMI:
      self.advance()
      if self.token.type == NEWLINE:
        self.advance()

      old_index = self.index
      try:
        if res := self.stmt():
          items.append(res)
      except errors.SyntaxError:
        self.reverse_to(old_index)

    return items

  def stmt(self) -> ASTNode:
    res = self.compound_stmt()
    if res:
      return res
    return self.simple_stmt()

  def compound_stmt(self) -> ASTNode:
    if self.token.matches(NAME, IF_KEYWORDS):
      return self.if_stmt()

  def simple_stmt(self) -> ASTNode:
    tok = None
    with self.try_register() as old_index:
      pos_start = self.token.pos_start.copy()
      var = self.primary()
      tok = self.token
    if tok is not None and (tok.type == EQUAL or tok.type in ASSIGNMENT_OP_DICT):
      return self.assignment(var, pos_start)
    else:
      self.reverse_to(old_index)

    if self.token.matches(NAME, DELETE_KEYWORDS):
      return self.del_stmt()
    node = self.star_expressions()
    if len(node.items) == 1:
      return node.items[0]
    return node

  def assignment(self, var, pos_start):
    def get_node(var, value):
      if isinstance(var, GetAttrNode):
        return SetAttrNode(var.object, var.attr_name, value, var.object.pos_start)
      if isinstance(var, GetItemNode):
        return SetItemNode(var.object, var.key, value, var.object.pos_start)
      return VarAssignNode(var, value)

    if self.token.type in ASSIGNMENT_OP_DICT:
      op = self.token
      op.type = ASSIGNMENT_OP_DICT[op.type]
      self.advance()
      value = self.expression()
      value = BinaryOpNode(var, op, value)
      return get_node(var, value)

    if self.token.type != EQUAL:
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'expected "="',
      )

    var_list = [var]
    value = None
    while self.token.type == EQUAL:
      self.advance()
      if self.token.type != NAME:
        value = self.expression()
        break
      var_list.append(self.atom())
    if value is None:
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'parser error',
      )
    if len(var_list) == 1:
      var = var_list[0]
      return get_node(var, value)
    return TupleNode(
      [get_node(var, value) for var in var_list], pos_start, self.token.pos_end.copy()
    )

  def star_expressions(self) -> TupleNode:
    pos_start = self.token.pos_start.copy()
    items = [self.star_expression()]
    while self.token.type == COMMA:
      self.advance()
      if self.token.type in (RPAR, RSQB):
        break
      items.append(self.star_expression())
    return TupleNode(items, pos_start, self.token.pos_end.copy())

  def star_expression(self) -> ASTNode:
    return self.expression()

  def expression(self) -> ASTNode:
    res = self.disjunction()
    if self.token.matches(NAME, IF_KEYWORDS):
      self.advance()
      condition = self.disjunction()
      if not self.token.matches(NAME, ELSE_KEYWORDS):
        raise errors.SyntaxError(
          self.token.pos_start,
          self.token.pos_end,
          'expected "else"',
        )
      self.advance()
      cases = [(condition, res)]
      else_block = self.expression()
      return IfNode(True, cases, else_block)

    if self.token.type == QUESTION:
      self.advance()
      value = self.disjunction()
      if self.token.type != COLON:
        raise errors.SyntaxError(
          self.token.pos_start,
          self.token.pos_end,
          'expected ":"',
        )
      self.advance()
      cases = [(res, value)]
      else_block = self.expression()
      return IfNode(True, cases, else_block)
    return res

  def disjunction(self):
    return self.bin_op({DOUBLEVBAR}, self.conjunction)

  def conjunction(self):
    return self.bin_op({DOUBLEAMPER}, self.inversion)

  def inversion(self):
    if self.token.type == EXCLAMATION:
      self.advance()
      return UnaryOpNode(EXCLAMATION, self.inversion())
    return self.comparison()

  def comparison(self):
    return self.bin_op(COMP_OP, self.bitwise_or)

  def bitwise_or(self):
    return self.bin_op(BITWISE_OR_OP, self.bitwise_xor)

  def bitwise_xor(self):
    return self.bin_op(BITWISE_XOR_OP, self.bitwise_and)

  def bitwise_and(self):
    return self.bin_op(BITWISE_AND_OP, self.shift_expr)

  def shift_expr(self):
    return self.bin_op(SHIFT_OP, self.sum)

  def sum(self):
    return self.bin_op(SUM_OP, self.term)

  def term(self):
    return self.bin_op(TERM_OP, self.factor)

  def factor(self):
    if self.token.type in UNARY_OP:
      op = self.token
      self.advance()
      return UnaryOpNode(op, self.factor())
    return self.power()

  def power(self):
    return self.bin_op(POWER_OP, self.primary)

  def primary(self, atom=None):
    pos_start = self.token.pos_start.copy()
    if atom is None:
      atom = self.atom()

    if self.token.type == DOT:
      self.advance()
      if self.token.type != NAME:
        raise errors.SyntaxError(
          self.token.pos_start,
          self.token.pos_end,
          'parser error',
        )
      tok = self.token
      self.advance()
      return self.primary(
        GetAttrNode(atom, tok, atom.pos_start.copy(), tok.pos_end.copy())
      )

    if self.token.type == LPAR:
      if not any(i.type == RPAR for i in self.tokens[self.index :]):
        raise errors.SyntaxError(
          self.token.pos_start, self.token.pos_end, "'(' was never closed"
        )
      self.advance()
      args, kwargs = self.arguments()
      if self.token.type != RPAR:
        raise errors.SyntaxError(
          self.token.pos_start, self.token.pos_end, 'expected ")"'
        )
      self.advance()
      return self.primary(
        CallNode(atom, args, kwargs, atom.pos_start.copy(), self.token.pos_end.copy())
      )

    if self.token.type == LSQB:
      if not any(i.type == RSQB for i in self.tokens[self.index :]):
        raise errors.SyntaxError(
          self.token.pos_start, self.token.pos_end, "'[' was never closed"
        )
      self.advance()
      key = self.slices()
      self.advance()
      return self.primary(GetItemNode(atom, key, pos_start, self.token.pos_end.copy()))
    return atom

  def arguments(self) -> tuple[TupleNode, DictNode]:
    if self.token.type == RPAR:
      return TupleNode(
        [], self.token.pos_start.copy(), self.token.pos_end.copy()
      ), DictNode({}, self.token.pos_start.copy(), self.token.pos_end.copy())

    pos_start = dict_pos_start = self.token.pos_start.copy()
    pos_end = None
    args = []
    kwargs = {}
    while self.token.type != RPAR:
      if self.token.type == NAME and self.lookahead().type == EQUAL:
        pos_end = dict_pos_start = self.token.pos_start.copy()
        kw = StringNode(self.token)
        self.advance()
        self.advance()
        kwargs[kw] = self.expression()
      if self.token.type == RPAR:
        break
      if self.token.type == COMMA:
        self.advance()
      elif self.token.type != RPAR:
        if kwargs:
          raise errors.SyntaxError(
            self.token.pos_start,
            self.token.pos_end,
            'positional argument follows keyword argument',
          )
        args.append(self.expression())
    return TupleNode(args, pos_start, pos_end), DictNode(
      kwargs, dict_pos_start, self.token.pos_end.copy()
    )

  def slices(self):
    return self.slice()

  def slice(self) -> SliceNode:
    pos_start = self.token.pos_start.copy()
    v1 = None
    if self.token.type != COLON:
      v1 = self.expression()
      if self.token.type != COLON:
        return v1
    self.advance()
    v2 = None
    if self.token.type not in {COLON, COMMA, RSQB}:
      v2 = self.expression()
    if self.token.type != COLON:
      return SliceNode(v1, v2, None, pos_start, self.token.pos_end.copy())
    self.advance()
    v3 = None
    if self.token.type not in {COLON, COMMA, RSQB}:
      v3 = self.expression()
    return SliceNode(v1, v2, v3, pos_start, self.token.pos_end.copy())

  def bin_op(self, operators, func):
    left = func()
    while self.token.type in operators:
      op = self.token
      self.advance()
      left = BinaryOpNode(left, op, func())
    return left

  def atom(self) -> ASTNode:
    tok = self.token
    if tok.type == COMMENT:
      self.advance()
      return CommentNode(tok)

    if tok.type in (NUMBER, STRING):
      self.advance()
      if tok.type == NUMBER:
        return NumberNode(tok)
      if tok.type == STRING:
        return StringNode(tok)
      raise errors.SyntaxError(
        tok.pos_start,
        tok.pos_end,
        'invalid single value',
      )

    if tok.type == NAME:
      self.advance()
      return VarAccessNode(tok)

    if tok.type == LPAR:
      return self.tuple_expr()

    if tok.type == LSQB:
      return self.list_expr()
    if tok.type == LBRACE:
      return self.dict_expr()

    raise errors.SyntaxError(
      self.token.pos_start,
      self.token.pos_end,
      f'invalid expr "{tok}"',
    )

  def tuple_expr(self) -> TupleNode:
    pos_start = self.token.pos_start.copy()
    if not any(i.type == RPAR for i in self.tokens[self.index :]):
      raise errors.SyntaxError(
        self.token.pos_start, self.token.pos_end, "'(' was never closed"
      )

    self.advance()
    if self.token.type == RPAR:
      self.advance()
      return TupleNode([], pos_start, self.token.pos_end.copy())

    node = self.star_expression()
    if self.token.type == RPAR:
      self.advance()
      return node
    if self.token.type != COMMA:
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'invalid syntax. Perhaps you forgot a comma?',
      )
    self.advance()
    if self.token.type == RPAR:
      self.advance()
      return TupleNode([node], pos_start, self.token.pos_end.copy())

    items = self.star_expressions().items
    if self.token.type != RPAR:
      raise errors.SyntaxError(pos_start, self.token.pos_end, "'(' was never closed")
    self.advance()
    return TupleNode([node] + items, pos_start, self.token.pos_end.copy())

  def list_expr(self) -> ListNode:
    if self.token.type != LSQB:
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'parser error',
      )
    if not any(i.type == RSQB for i in self.tokens[self.index :]):
      raise errors.SyntaxError(
        self.token.pos_start, self.token.pos_end, "'[' was never closed"
      )

    pos_start = self.token.pos_start.copy()
    self.advance()
    if self.token.type == RSQB:
      self.advance()
      return ListNode([], pos_start, self.token.pos_end)

    items = self.star_expressions().items
    if self.token.type != RSQB:
      raise errors.SyntaxError(self.token.pos_start, self.token.pos_end, 'expected "]"')
    self.advance()
    return ListNode(items, pos_start, self.token.pos_end.copy())

  def dict_expr(self) -> DictNode:
    if self.token.type != LBRACE:
      raise errors.SyntaxError(self.token.pos_start, self.token.pos_end, 'parser error')
    if not any(i.type == RBRACE for i in self.tokens[self.index :]):
      raise errors.SyntaxError(
        self.token.pos_start, self.token.pos_end, "'{' was never closed"
      )

    pos_start = self.token.pos_start.copy()
    self.advance()
    if self.token.type == RBRACE:
      self.advance()
      return DictNode({}, pos_start, self.token.pos_end)

    items = self.double_starred_kvpairs()
    if self.token.type != RBRACE:
      raise errors.SyntaxError(self.token.pos_start, self.token.pos_end, 'expected "}"')
    self.advance()
    return DictNode(items, pos_start, self.token.pos_end.copy())

  def double_starred_kvpairs(self) -> dict[ASTNode, ASTNode]:
    k, v = self.double_starred_kvpair()
    items = {k: v}
    while self.token.type == COMMA:
      self.advance()
      if self.token.type == RBRACE:
        break
      k, v = self.double_starred_kvpair()
      items[k] = v
    return items

  def double_starred_kvpair(self) -> tuple[ASTNode, ASTNode]:
    return self.kvpair()

  def kvpair(self) -> tuple[ASTNode, ASTNode]:
    k = self.expression()
    if self.token.type != COLON:
      raise errors.SyntaxError(self.token.pos_start, self.token.pos_end, 'expected ":"')
    self.advance()
    v = self.expression()
    return k, v

  def del_stmt(self):
    if not self.token.matches(NAME, DELETE_KEYWORDS):
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'parser error',
      )

    pos_start = self.token.pos_start.copy()
    self.advance()
    var = self.token
    if var.type != NAME:
      if var.type in (ENDMARKER, NEWLINE):
        raise errors.SyntaxError(
          var.pos_start,
          var.pos_end,
          'parser error',
        )
      raise errors.SyntaxError(var.pos_start, var.pos_end, 'cannot delete literal')
    self.advance()
    if self.token.type != COMMA:
      return VarDeleteNode(var, pos_start, var.pos_end.copy())

    var_list = [var]
    while self.token.type == COMMA:
      self.advance()
      var = self.token
      if var.type in (ENDMARKER, NEWLINE):
        raise errors.SyntaxError(
          var.pos_start,
          var.pos_end,
          'parser error',
        )
      if var.type != NAME:
        raise errors.SyntaxError(var.pos_start, var.pos_end, 'cannot delete literal')
      var_list.append(var)
      self.advance()
    return VarDeleteNode(var_list, pos_start, self.token.pos_end.copy())

  def if_stmt(self):
    pos_start = self.token.pos_start.copy()
    self.advance()

    orelse = None
    lpar_test = self.token.type == LPAR
    test = self.expression()
    lbrace_block = self.token.type == LBRACE
    if not lpar_test and self.token.type != COLON and self.token.type != LBRACE:
      raise errors.SyntaxError(
        self.token.pos_start, self.token.pos_end, 'expected ":" or "{"'
      )
    if self.token.type == COLON:
      self.advance()

    body = self.block('if', pos_start, lpar_test and not lbrace_block)
    if self.token.type == NEWLINE and self.lookahead().matches(NAME, ELIF_KEYWORDS):
      self.advance()
      orelse = [self.if_stmt()]
    elif self.token.type == NEWLINE and self.lookahead().matches(NAME, ELSE_KEYWORDS):
      self.advance()
      orelse = self.else_block()

    return IfNode(
      test,
      body,
      orelse,
      pos_start,
      self.token.pos_end.copy(),
    )

  def else_block(self):
    pos_start = self.token.pos_start.copy()
    self.advance()

    if self.token.type != COLON:
      raise errors.SyntaxError(
        self.token.pos_start,
        self.token.pos_end,
        'expected ":"',
      )
    self.advance()
    return self.block('else', pos_start, False)

  def block(self, name, pos_start, aline=False) -> list[ASTNode]:
    pos_start = self.token.pos_start.copy()
    lbrace_block = self.token.type == LBRACE
    if lbrace_block:
      self.advance()

    if lbrace_block or self.token.type == NEWLINE:
      if self.token.type == NEWLINE:
        self.advance()
      if not lbrace_block and self.token.type != INDENT:
        raise errors.IndentationError(
          pos_start,
          self.token.pos_end,
          f'expected an indented block after {name} definition',
          self.token.pos_start,
          self.token.pos_end,
        )
      # endif
      if self.token.type == INDENT:
        indent = self.token.value
        self.advance()
      # endif
      if lbrace_block and self.token.type == RBRACE:
        self.advance()
        return []

      res = self.statements()
      if not res:
        raise errors.IndentationError(
          pos_start,
          self.token.pos_end,
          f'expected an indented block after {name} definition',
          self.token.pos_start,
          self.token.pos_end,
        )
      # endif

      if not lbrace_block:
        if self.token.type != DEDENT or self.token.value != indent:
          raise errors.IndentationError(
            pos_start,
            self.token.pos_end,
            'unexpected indent',
            self.token.pos_start,
            self.token.pos_end,
          )
      if self.token.type == DEDENT:
        self.advance()

      if lbrace_block:
        if self.token.type == NEWLINE:
          self.advance()
        if self.token.type != RBRACE:
          raise errors.SyntaxError(
            pos_start, self.token.pos_end, "'{' was never closed"
          )
        self.advance()
      return res.items
    # endif

    if aline:
      return [self.stmt()]
    return self.stmts()
