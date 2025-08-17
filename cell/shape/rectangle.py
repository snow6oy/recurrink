from shapely.geometry import Polygon
class Rectangle:

  VERBOSE = False

  def __init__(self, name):
    self.name = name

  def coords(self, dim, kwargs):
    ''' calculate bounding coords for a Shapely polygon
    '''
    X, Y, W, H, a, b, c, d, A, B, C, D = dim

    rectgl = None
    shape  = kwargs['name']
    size   = kwargs['size']
    facing = kwargs['facing']
    sizes  = {
      'square': {
        'small': [a, b, c, d],
       'medium': [X, Y, W, H],
        'large': [A, B, C, D]
      },
      'line': {
        'medium': {
          'N': [a, Y, c, H],
          'S': [a, Y, c, H],
          'E': [X, b, W, d],
          'W': [X, b, W, d]
        },
        'small': {  # TODO same as small square so deprecate in the interface
          'N': [a, b, c, d],
          'S': [a, b, c, d],
          'E': [a, b, c, d],
          'W': [a, b, c, d]
        },
        'large': {
          'N': [a, B, c, D],
          'S': [a, B, c, D],
          'W': [A, b, C, d],
          'E': [A, b, C, d]
        }
      },
      'edge': {
        'small': {
          'N': [X, d, c, H],
          'S': [a, Y, W, b],
          'E': [W, b, c, H],
          'W': [X, Y, a, d]
        }
      }
    }
    """
          'south': [a, Y, c, H],
          'north': [a, Y, c, H],
           'east': [X, b, W, d],
           'west': [X, b, W, d],
          'north': [a, b, c, d], 
          'south': [a, b, c, d],
           'east': [a, b, c, d],
           'west': [a, b, c, d],
         'north': [a, B, c, D],
         'south': [a, B, c, D],
          'west': [A, b, C, d],
          'east': [A, b, C, d],
          'south': [a, Y, W, b],
          'north': [X, d, c, H],
           'east': [W, b, c, H],
           'west': [X, Y, a, d],
    """
    if shape in sizes and size in sizes[shape]:
      if shape == 'square':
        x, y, w, h = sizes[shape][size]
        rectgl = Polygon(((x, y), (x, h), (w, h), (w, y)))
      elif shape == 'sqring':
        X, Y, W, H = sizes['square']['medium']
        x, y, w, h = sizes['square']['small']
        rectgl = Polygon(
          ((X, Y), (X, H), (W, H), (W, Y)), 
          holes=[((x, y), (x, h), (w, h), (w, y))]
        )
      elif facing in sizes[shape][size]:
        x, y, w, h = sizes[shape][size][facing]
        rectgl = Polygon(((x, y), (x, h), (w, h), (w, y)))
      else:
        raise NotImplementedError(f'{shape=} {size=} {facing=}')
    else: 
      raise NotImplementedError(f'{shape=} {size=}')

    if self.VERBOSE: print(f'{shape=} {size=} {facing=} {x} {y} {w} {h}')
    return rectgl

  def guide(self, direction):
    ''' expand facing to a pair of guidelines for meander
    '''
    control = {
      'C': ('spiral', None), 
      'N': ('guided', 'EB', 'ET'),
      'S': ('guided', 'EB', 'ET'),
      'E': ('guided', 'SL', 'SR'),
      'W': ('guided', 'NL', 'NR')
    }
    """
        'all': ('spiral', None), 
      'north': ('guided', 'EB', 'ET'),
      'south': ('guided', 'EB', 'ET'),
       'east': ('guided', 'SL', 'SR'),
       'west': ('guided', 'NL', 'NR'),
    """
    if direction in control: return control[direction]
    else: # abandon if there are no guidelines defined
      raise KeyError(f'all at sea > {direction=} {self.name=} not found')

  def validate(self, geom):
   if geom['name'] == 'square' and geom['facing'] != 'C': 
     return 'must face center'


'''
the
end
'''
