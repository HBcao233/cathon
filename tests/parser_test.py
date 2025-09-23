from cathon.lexer import Lexer
from cathon.parser import Parser


file = 'tests/test.cat'
with open(file, 'r') as f:
  lexer = Lexer(file, f.read())
tokens = lexer.parse()
ast = Parser(tokens).parse()
print(ast)
