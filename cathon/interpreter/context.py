class Context(object):
  def __init__(self, display_name, parent=None, parent_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_pos = parent_pos
    self.symbol_table = None
    