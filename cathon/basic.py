from .constants import *
from .lexer.lexer import Lexer 
from .parser.parser import Parser
from .interpreter import (
  Interpreter, 
  Context, 
  SymbolTable, 
  Builtin_Function_Or_Method,
  values
)


global_symbol_table = SymbolTable()


def set_builtins():
  g = global_symbol_table
  g.set('null', values.null)
  g.set('Inf', values.Float(float('inf')))
  g.set('NaN', values.Float(float('nan')))
  g.set('type', values.cat_type)
  g.set('object', values.cat_object)
  g.set('bool', values.Bool.CAT__class__)
  g.set('int', values.Int.CAT__class__)
  g.set('float', values.Float.CAT__class__)
  g.set('str', values.String.CAT__class__)
  g.set('list', values.List.CAT__class__)
  g.set('tuple', values.Tuple.CAT__class__)
  g.set('dict', values.Dict.CAT__class__)
  
  for names, func in BUILTINS_FUNC.items():
    assert isinstance(names, tuple), "item of BUILTINS_FUNC must be a tuple"
    
    func_name = names[0]
    if isinstance(func, str):
      func = getattr(values, func)
    for k in names:
      g.set(k, Builtin_Function_Or_Method(func, func_name))


def run(file, code):
  set_builtins()
  
  lexer = Lexer(file, code)
  tokens = lexer.parse()
  ast = Parser(tokens).parse()
  context = Context('<module>')
  context.symbol_table = global_symbol_table
  return Interpreter.visit(ast, context)
