from cat.lexer import Lexer 


file = 'tests/test.cat'
with open(file, 'r') as f:
  lexer = Lexer(file, f.read())
tokens = lexer.parse()
print(tokens)
