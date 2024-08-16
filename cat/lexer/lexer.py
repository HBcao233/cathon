from ..constants import * 
from .tokens import Token
from .position import Position
from .. import errors


class Lexer(object):
  def __init__(self, file: str, code: str):
    self.file, self.code = file, code
    self.char = None
    self.pos = Position(-1, 0, -1, file, code)
    self.advance()
    self.indents = []
    self.indent_type = None
    
  def advance(self, count=1):
    while (count := count - 1) >= 0:
      self.pos.advance(self.char)
      self.update()
    
  def update(self):
    if self.pos.index >= len(self.code):
      self.char = None 
    else:
      self.char = self.code[self.pos.index]
      
  def reverse_to(self, pos):
    self.pos = pos
    self.update()
    
  def lookahead(self, count=1):
    index = self.pos.index + count
    if index >= len(self.code):
      return None 
    return self.code[index]
  
  def parse(self) -> list[Token]:
    res = []
    brackets_nl = ''
    while self.char:
      if self.char == '#':
        self.skip_comment()
        continue
     
      if len(res) == 0 or self.char == '\n':
        tokens = self.make_indent()
        if len(res) != 0:
          res.append(Token(NEWLINE, pos_start=self.pos))
        if tokens: 
          if len(res) == 0:
            raise errors.IndentationError(self.pos, self.pos, 'unexpected indent')
          res.extend(tokens)
        if len(res) != 0:
          i = 1 
          while self.lookahead(i) in (' ', '\t'):
            i += 1
          if self.lookahead(i) in (None, '\n'):
            self.advance()
            continue 
      if self.char == ' ':
        self.advance()
        continue
      
      if self.lookahead() == '\n':
        if self.char == '(':
          brackets_nl = ')'
        if self.char == '[':
          brackets_nl = ']'
        if self.char == '{':
          brackets_nl = '}'
      if self.char == brackets_nl:
        brackets_nl = ''
      
      if self.char == '\\':
        token = Token(NL, pos_start=self.pos)
        self.advance()
      elif (
        (DIGITS(self.char) and self.char != '.') or 
        (self.char == '.' and self.lookahead() and DIGITS(self.lookahead()) and self.lookahead() != '.')
      ):
        token = self.make_number()
      elif self.char == '.':
        token = self.make_dots()
      elif self.char in OP_DICT:
        token = self.make_opertor()
      elif self.char in STRING_FLAG:
        token = self.make_string(self.char)
      elif LETTERS(self.char):
        token = self.make_name()
      else:
        pos_start = self.pos.copy()
        char = self.char
        self.advance()
        raise errors.SyntaxError(pos_start, self.pos, f"invalid character '{char}' (U+{hex(ord(char))})")
      res.append(token)
      if brackets_nl:
        res.append(Token(NL, pos_start=self.pos)) 
    
    while self.indents:
      res.append(Token(DEDENT, len(self.indents), pos_start=self.pos))
      self.indents.pop()
    
    i = 0
    while i < len(res) - 1:
      if res[i].type == NEWLINE and res[i+1].type == DEDENT:
        res[i:i+2] = (res[i:i+2])[::-1]
      elif res[i].type == NEWLINE and res[i+1].type == NEWLINE:
        i -= 1 
        res.pop(i+1)
      i += 1
    
    res.append(Token(ENDMARKER, pos_start=self.pos))
    return res
    
  def skip_comment(self):
    self.advance()
    while self.char and self.char != '\n':
      self.advance()
      
  def make_indent(self):
    if self.char == '\n':
      self.advance()
      '''
        i = 1
        while self.lookahead(i) == ' ':
          i += 1
        if self.lookahead(i) in ('\n',None):
          self.advance()
          continue
      '''
        
    count = 0
    pos_start = self.pos.copy()
    while self.char and self.char in (' ', '\t'):
      if self.indent_type == None:
        self.indent_type = self.char
      elif self.indent_type != self.char:
        raise errors.TabError(
          self.pos, self.pos,
          'inconsistent use of tabs and spaces in indentation'
        )
      count += 1
      self.advance()
    res = []
    while self.indents:
      if count >= self.indents[-1]:
        break
      res.append(Token(DEDENT, len(self.indents), self.pos))
      self.indents.pop()
    
    if count:
      flag = self.indents.count(count) == 0
      if self.lookahead() == NEWLINE:
        flag = False
      if not self.indents or count > self.indents[-1]:
        self.indents.append(count)
      if flag:
        res.append(Token(INDENT, len(self.indents), pos_start, self.pos))
    return res
  
  def make_number(self) -> Token:
    pos_start = self.pos.copy()
    if self.char == '0' and self.lookahead() == 'b':
      self.advance(2)
      num = self.make_num(2)
    elif self.char == '0' and self.lookahead() == 'x':
      self.advance(2)
      num = self.make_num(16)
    else:
      num = self.make_num(10)
    return Token(NUMBER, num, pos_start, self.pos)
  
  def make_num(self, base=10):
    bases = {
      2: ('binary', BIN_DIGITS),
      10: ('decimal', DIGITS),
      16: ('hexadecimal', HEX_DIGITS),
    }
    num = []
    pos_start = self.pos.copy()
    is_float = False
    while self.char and (
      LETTERS_DIGITS(self.char) or 
      self.char in ['_', '.']
    ):
      if self.char == '.':
        is_float = True
      if self.char == '_':
        self.advance()
        continue
      elif not bases[base][1](self.char):
        self.advance()
        raise errors.SyntaxError(pos_start, self.pos, f'invalid {bases[base][0]} literal')
      num.append(self.char)
      self.advance()
    num = ''.join(num)
    if not num:
      self.advance()
      raise errors.SyntaxError(pos_start, self.pos, f'invalid {bases[base][0]} literal')
      
    if is_float:
      return float(num)
    return int(num, base)
    
  def make_dots(self):
    pos_start = self.pos.copy()
    self.advance()
    count = 1
    while self.char == '.':
      self.advance()
      count += 1
    if count == 1:
      return Token(DOT, None, pos_start, self.pos)
    if count == 3:
      return Token(ELLIPSIS, None, pos_start, self.pos)
    raise errors.SyntaxError(pos_start, self.pos)
  
  def make_opertor(self) -> Token:
    def get_op(dict_, res=None):
      if isinstance(dict_, tuple):
        res = dict_[0] or res
        dict_ = dict_[1]
      if self.char in dict_:
        res = dict_.get(self.char)
        self.advance()
      if isinstance(res, dict):
        res = (None, res)
      if isinstance(res, tuple):
        res, dict_ = res
        return get_op(dict_, res)
      return res
    
    pos_start = self.pos.copy()
    res = get_op(OP_DICT)
    if res is None:
      self.reverse_to(pos_start)
      return self.make_name()
    return Token(res, pos_start=pos_start, pos_end=self.pos)
      
  def make_string(self, quotation) -> Token:
    res = []
    pos_start = self.pos.copy()
    escape_character = False
    
    self.advance()
    while (
      ((quotation not in ('“', '”')) and self.char != quotation) or
      (quotation in ('“', '”') and self.char not in ('“', '”'))
    ) or escape_character:
      if self.char is None or self.char == '\n':
        raise errors.SyntaxError(self.pos, self.pos, f'unterminated string literal (excepted {repr(quotation)} )')
      if escape_character:
        res.append(ESCAPE_CHAR.get(self.char, self.char))
        escape_character = False
        self.advance()
        continue
      if self.char == '\\' and quotation != '`':
        escape_character = True
        self.advance()
        continue
      res.append(self.char)
      self.advance()
    self.advance()
    return Token(STRING, ''.join(res), pos_start, self.pos)
  
  def make_name(self) -> Token:
    res = []
    pos_start = self.pos.copy()
    res.append(self.char)
    self.advance()
    while self.char and LETTERS_DIGITS(self.char):
      res.append(self.char)
      self.advance()
    res = ''.join(res)
    
    if res in SPECIAL_KEYWORDS:
      tok_type, tok_value = SPECIAL_KEYWORDS[res]
      return Token(tok_type, tok_value, pos_start, self.pos)
    elif res in KEYWORDS:
      return Token(NAME, res, pos_start, self.pos)
    return Token(NAME, res, pos_start, self.pos)
    