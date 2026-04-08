import pprint
from .shape import *
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class InputValidator:
  ''' Validate input geometries by calling shape.*.validate

      to be merged with Pydantic in block.validator
  '''
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)

  def __init__(self, ver=None):
    self.ver      = ver # None is not a good default (better to override)
    self.uniqfill = set() # recurrink.build will hydrate

  def validate(self, label, cell):
    ''' raise error unless given data exists in palette
    '''
    if 'geom' in cell:
      self.geometry(label, cell['geom']) 
    if 'color' in cell:
      fg = cell['color']['fill']
      op = float(cell['color']['opacity'])
      bg = cell['color']['background']
      if op < 0 or op > 1: 
        raise ValueError(f"validation error: >{label}< {op=} not ok {self.ver}")
      elif fg not in self.uniqfill:
        raise ValueError(f"validation error: >{label}< {fg=} not in {self.ver}")
      elif bg and bg not in self.uniqfill:
        raise ValueError(f"validation error: >{label}< {bg=} not in {self.ver}")
    if 'stroke' in cell and cell['stroke']: 
      f = cell["stroke"]['fill']
      if f not in self.uniqfill:
        raise ValueError(f"cell: >{label}< {f} stroke not in {self.ver}")

  def geometry(self, label, geom):
    if 'name' in geom: name = geom['name']
    else: raise ValueError(f"validation error: {label}")

    shapes = {
         'line': Rectangle(name),
         'edge': Rectangle(name),
       'square': Rectangle(name),
       'sqring': Rectangle(name),
       'gnomon': Gnomon(),
      'parabol': Parabola(),
      'triangl': Triangle(),
      'diamond': Diamond(),
       'circle': Circle()
    }
    shape  = shapes[name]
    errmsg = shape.validate(geom)
    if errmsg: raise ValueError(f"validation error {label}: {name} {errmsg}")
'''
the
end
'''
