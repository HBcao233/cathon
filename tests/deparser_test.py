from cathon import (
  Lexer,
  Parser,
  Deparser,
  errors,
)


if __name__ == '__main__':
  file = 'tests/test.cat'
  with open(file, 'r') as f:
    lexer = Lexer(file, f.read())
  try:
    tokens = lexer.parse()
    ast = Parser(tokens).parse()
  except errors.BaseError as e:
    print(e)
    exit()
  res = Deparser.visit(ast, Deparser.Context(0))
  print(res)
