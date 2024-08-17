class SymbolTable(object):
  class Undefined(object):
    def __repr__(self):
      return 'undefined'
      
    def get(self):
      return self
      
  undefined = Undefined()
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent
  
  def get(self, name):
    value = self.symbols.get(name, self.undefined)
    if value is self.undefined and self.parent:
      return self.parent.get(name)
    return value
  
  def set(self, name, value):
    self.symbols[name] = value
    
  def remove(self, name):
    if name not in self.symbols:
      return self.undefined
    return self.symbols.pop(name)
    
  def exist(self, name):
    return name in self.symbols
