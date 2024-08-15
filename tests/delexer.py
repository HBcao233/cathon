from cat.lexer import Lexer
from cat.constants import *


class Delexer:
  def __init__(self, tokens):
    self.tokens = tokens
    self.index = -1
    self.advance()
  
  def advance(self):
    self.index += 1
    self.update()
  
  def update(self):
    if self.index >= len(tokens):
      self.token = None
    else:
      self.token = tokens[self.index]
      
  def lookahead(self, count=1):
    index = self.index + count
    if index >= len(tokens):
      return None
    return tokens[index]
  
  def parse(self):
    res = []
    indent = 0
    while self.token:
      type, value = self.token.type, self.token.value
      if type in OP_REDICT:
        if type in (COLON, LPAR, RSQB) and res[-1] == ' ':
          res.pop()
        res.extend(OP_REDICT[type])
        if type not in (LPAR, LSQB):
          res.extend(' ')
      
      if type == DEDENT:
        indent -= 1
      if type == INDENT:
        indent += 1
        res.extend('\t')
      if type == NEWLINE:
        res.extend('\n')
        if indent:
          res.extend('\t' * indent)
        # if self.tokens[self.index-1].type == DEDENT:
         # res.extend('\t')
      if type == NL:
        if self.lookahead().type == NEWLINE:
          self.advance()
      
      if type in (NAME, NUMBER):
        res.extend(str(value))
        if res[-1] != '(' and self.lookahead().type != RPAR:
          res.append(' ')
        
      if type == STRING:
        if type in (LPAR, ) and res[-1] == ' ':
          res.pop()
        res.extend(repr(value))
      self.advance()
    return ''.join(res)
    
if __name__ == '__main__':
  file = 'tests/test.cat'
  with open(file, 'r') as f:
    lexer = Lexer(file, f.read())
  tokens = lexer.parse()
  print(Delexer(tokens).parse())
