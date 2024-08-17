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
  null, cat_type, cat_object,
  Type, Object, Bool,
  Int, Float, String, Tuple,
  List, Dict
)


global_symbol_table = SymbolTable()


def set_builtins():
  g = global_symbol_table
  g.set('Inf', Float(float('inf')))
  g.set('NaN', Float(float('nan')))
  g.set('null', null)
  g.set('type', cat_type)
  g.set('object', cat_object)
  g.set('bool', Bool.CAT__class__)
  g.set('int', Int.CAT__class__)
  g.set('float', Float.CAT__class__)
  g.set('str', String.CAT__class__)
  g.set('list', List.CAT__class__)
  g.set('tuple', Tuple.CAT__class__)
  g.set('dict', Dict.CAT__class__)
  
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
