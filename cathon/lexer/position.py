class Position(object):
  def __init__(self, index: int, line: int, column: int, file: str, code: str):
    self.index = index
    self.line = line
    self.column = column
    self.file = file
    self.code = code
    
  def advance(self, char: str = None):
    self.index += 1
    self.column += 1
    
    if char == '\n':
      self.column = 0
      self.line += 1
      
  def copy(self):
    return Position(self.index, self.line, self.column, self.file, self.code)
    