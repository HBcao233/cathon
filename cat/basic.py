import builtins
from .constants import *
from .lexer.lexer import Lexer 
from .parser.parser import Parser
from .interpreter import (
  Interpreter, 
  Context, 
  SymbolTable, 
  Builtin_Function_Or_Method,
)
from .interpreter.values import (
  Number, null, meta, value_meta
)


global_symbol_table = SymbolTable()


def set_builtins():
  g = global_symbol_table
  g.set('Inf', Number(float('inf')))
  g.set('NaN', Number(float('nan')))
  g.set('null', null)
  g.set('type', meta)
  g.set('object', value_meta)
  
  for names in BUILTINS_FUNC:
    assert isinstance(names, tuple), "item of BUILTINS_FUNC must be a tuple"
    
    func_name = names[0]
    for k in names:
      g.set(k, Builtin_Function_Or_Method(getattr(builtins, func_name)))


def run(file, code):
  set_builtins()
  
  lexer = Lexer(file, code)
  tokens = lexer.parse()
  ast = Parser(tokens).parse()
  context = Context('<module>')
  context.symbol_table = global_symbol_table
  return Interpreter.visit(ast, context)
