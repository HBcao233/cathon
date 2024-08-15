from cat.lexer import Lexer 
from cat.parser import Parser 


file = 'tests/test.cat'
with open(file, 'r') as f:
  lexer = Lexer(file, f.read())
tokens = lexer.parse()
ast = Parser(tokens).parse()
print(ast)
