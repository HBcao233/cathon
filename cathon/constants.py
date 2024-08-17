import re 
from itertools import chain
from .token import *
from .token import EXACT_TOKEN_TYPES


NOT_MATCH = r'(?!（|）|“|”|：|，)'
DIGITS = re.compile(r'[0-9.]').match
BIN_DIGITS = re.compile(r'[01]').match
HEX_DIGITS = re.compile(r'[0-9a-fA-F]').match
LETTERS = re.compile(NOT_MATCH+r'([a-zA-Z_\$]|[^\u0000-\u007F])').match
LETTERS_DIGITS = re.compile(NOT_MATCH+r'([0-9a-zA-Z_\$]|[^\u0000-\u007F])').match


BUILTINS = {
  '与', '或', '非',
  'Inf', 'NaN', 'exit', 
}
BUILTINS_FUNC: dict[tuple, callable] = {
  ('print', '打印'): print,
  ('getattr', '取属性'): 'cat_getattr',
  ('abs', '绝对值'): 'cat_abs',
  ('len', '长度'): 'cat_len',
  # ('repr', ): 'cat_repr',
  # ('all', '全都'): all,
  # ('ascii', ): ascii,
  # ('any', '存在'): 'cat_any',
}
BUILTINS |= set(chain.from_iterable(BUILTINS_FUNC))

COMP_OP = { EQEQUAL, NOTEQUAL, LESS, GREATER, LESSEQUAL, GREATEREQUAL }
BITWISE_OR_OP = { VBAR }
BITWISE_XOR_OP = { CIRCUMFLEX }
BITWISE_AND_OP = { AMPER }
SHIFT_OP = { LEFTSHIFT, RIGHTSHIFT }

SUM_OP = { PLUS, MINUS }
TERM_OP = { STAR, SLASH, DOUBLESLASH, PERCENT, AT }
POWER_OP = { DOUBLESTAR }
UNARY_OP = { PLUS, MINUS, TILDE }

ASSIGNMENT_OP = {
  PLUSEQUAL, MINEQUAL, 
  STAREQUAL, SLASHEQUAL, PERCENTEQUAL, 
  AMPEREQUAL, VBAREQUAL, CIRCUMFLEXEQUAL, 
  LEFTSHIFTEQUAL, RIGHTSHIFTEQUAL, 
  DOUBLESTAREQUAL, DOUBLESLASHEQUAL
}
ASSIGNMENT_OP_DICT = {
  PLUSEQUAL: PLUS,
  MINEQUAL: MINUS,
  STAREQUAL: STAR,
  SLASHEQUAL: SLASH,
  PERCENTEQUAL: PERCENT,
  AMPEREQUAL: AMPER,
  VBAREQUAL: VBAR,
  CIRCUMFLEXEQUAL: CIRCUMFLEX,
  LEFTSHIFTEQUAL: LEFTSHIFT,
  RIGHTSHIFTEQUAL: RIGHTSHIFT,
  DOUBLESTAREQUAL: DOUBLESTAR,
  DOUBLESLASHEQUAL: DOUBLESLASH,
}
OP_DICT = {
  '!': (EXCLAMATION, {'=': NOTEQUAL}),
  '%': (PERCENT, {'=': PERCENTEQUAL}),
  '&': (AMPER, {'=': AMPEREQUAL, '&': DOUBLEAMPER}),
  '*': (STAR, {
    '*': (DOUBLESTAR, {'=': DOUBLESTAREQUAL}),
    '=': STAREQUAL,
  }),
  '+': (PLUS, {'=': PLUSEQUAL}),
  '-': (MINUS, {'=', MINEQUAL}),
  '/': (SLASH, {
    '/': (DOUBLESLASH, {'=': DOUBLESLASHEQUAL}),
    '=': SLASHEQUAL,
  }),
  '<': (LESS, {
    '<': (LEFTSHIFT, {'=': LEFTSHIFTEQUAL}),
    '=': LESSEQUAL,
    '>': NOTEQUAL,
  }),
  '=': (EQUAL, {'=': EQEQUAL}),
  '>': (GREATER, {
    '>': (RIGHTSHIFT, {'=': RIGHTSHIFTEQUAL}),
    '=': GREATEREQUAL,
  }),
  '^': (CIRCUMFLEX, {'=': CIRCUMFLEXEQUAL}), 
  '|': (VBAR, {'=': VBAREQUAL, '|': DOUBLEVBAR}),
  '~': TILDE,
  '(': LPAR,
  ')': RPAR,
  '[': LSQB,
  ']': RSQB,
  '{': LBRACE,
  '}': RBRACE,
  ',': COMMA,
  '->': RARROW,
  ':': COLON,
  ':=': COLONEQUAL,
  ';': SEMI,
  '@': AT,
  '@=': ATEQUAL,
  '?': QUESTION,
  '赋': {'值': EQUAL},
  '为': EQEQUAL,
  '等': {'于': EQEQUAL},
  '不': {
    '为': NOTEQUAL, 
    '等': {'于': NOTEQUAL},
  },
  '小': {
    '于': (LESS, {'等': {'于': LESSEQUAL}}),
  },
  '大': {
    '于': (GREATER, {'等': {'于': GREATEREQUAL}}),
  },
  '与': DOUBLEAMPER,
  '或': DOUBLEVBAR,
  '非': EXCLAMATION,
  '（': LPAR,
  '）': RPAR,
  '，': COMMA,
  '：': COLON,
  '～': TILDE,
  '？': QUESTION,
}
OP_REDICT = {v: k for k, v in EXACT_TOKEN_TYPES.items()}

STRING_FLAG = {'"', "'", '`', '“', '”'}
ESCAPE_CHAR = {
  'n': '\n',
  't': '\t',
  'a': '\a',
  'v': '\v',
  'r': '\r',
  '\\': '\\',
}

SPECIAL_KEYWORDS = {
  'true': (NUMBER, True),
  'false': (NUMBER, False),
  'and': (DOUBLEAMPER, None),
  'or': (DOUBLEVBAR, None),
  'not': (EXCLAMATION, None),
  '真': (NUMBER, True),
  '假': (NUMBER, False),
}

DELETE_KEYWORDS = {'del', '删除'}
IF_KEYWORDS = ('if', '若', '如果')
ELIF_KEYWORDS = ('elif', '又若', '又如')
ELSE_KEYWORDS = ('else', '否则', '不然')

KEYWORDS = {
  'exit', 'pass', 
}
KEYWORDS |=  DELETE_KEYWORDS | set(IF_KEYWORDS) | set(ELIF_KEYWORDS) | set(ELSE_KEYWORDS)
