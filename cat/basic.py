import builtins
from .lexer.lexer import Lexer 
from .parser.parser import Parser
from .interpreter import Interpreter, Context, SymbolTable, values, Builtin_Function_Or_Method
from .constants import *

global_symbol_table = SymbolTable()


def set_builtins():
  global_symbol_table.set('Inf', values.Number(float('inf')))
  global_symbol_table.set('NaN', values.Number(float('nan')))
  global_symbol_table.set('null', values.Null())
  
  for names, v in BUILTINS_FUNC.items():
    if not isinstance(names, tuple):
      names = (names, )
    if isinstance(v, tuple):
      func_name, as_name = v
    else:
      if not v:
        v = names[0]
      func_name = as_name = v
    for k in names:
      global_symbol_table.set(k, Builtin_Function_Or_Method(getattr(builtins, func_name), as_name))
  
  
def run(file, code):
  set_builtins()
  
  lexer = Lexer(file, code)
  tokens = lexer.parse()
  ast = Parser(tokens).parse()
  context = Context('<module>')
  context.symbol_table = global_symbol_table
  return Interpreter.visit(ast, context)
