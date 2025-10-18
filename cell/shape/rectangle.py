from shapely.geometry import Polygon, LineString
from cell.meander import Line
from cell.spiral import Spiral

class Rectangle(Line):

  VERBOSE = False

  def __init__(self, name):
    self.name = name

  def validate(self, geom):
   if geom['name'] == 'square' and geom['facing'] != 'C': 
     return 'must face center'

  def draw(self, clen, dim, geom):
    ''' rectangle interface to meander
        when called and Linear:True
        returns a Shapely.LineString
    '''
    bounds = self.coords(dim, size=geom['size'], facing=geom['facing'])
    linstr = LineString()

    if self.name == 'spiral':
      spiral  = Spiral()
      linstr = LineString(spiral.make(clen, bounds))
    elif self.name == 'sqring':
      # TODO split bounds and orchestrate calls to meander
      # see parabola for inspiration
      linstr = LineString()
    else:
      facing  = geom['facing']
      guideln = self.guidelines(facing, clen, bounds)
      points  = self.collectPoints(guideln)
      linstr = self.makeStripes(points)
    return linstr

  def paint(self, dim, kwargs):
    ''' rectangle in Surface mode
        returns a Shapely.polygon
    '''
    rectgl = None
    coords = self.coords(dim, size=kwargs['size'], facing=kwargs['facing'])
    if len(coords) > 4:
      X, Y, W, H, x, y, w, h = coords
      rectgl = Polygon(
        ((X, Y), (X, H), (W, H), (W, Y)), 
        holes=[((x, y), (x, h), (w, h), (w, y))]
      )
    elif len(coords) == 4:
      x, y, w, h = coords
      rectgl     = Polygon(((x, y), (x, h), (w, h), (w, y)))
    return rectgl

  def coords(self, dim, size, facing):
    ''' calculate bounding coords for a Shapely polygon
    '''
    X, Y, W, H, a, b, c, d, A, B, C, D = dim

    coords = None
    sizes  = {
      'square': {
        'small': [a, b, c, d],
       'medium': [X, Y, W, H],
        'large': [A, B, C, D]
      },
      'spiral': {   # just an alias for square
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
        'small': {  # same as small square. could deprecate in the interface
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
    if self.name == 'sqring':
      coords = sizes['square']['medium'] + sizes['square']['small']
    elif self.name in sizes and size in sizes[self.name]:
      if self.name == 'square' or self.name == 'spiral':
        coords = sizes[self.name][size]
      elif facing in sizes[self.name][size]:
        coords = sizes[self.name][size][facing]
      else:
        raise NotImplementedError(f'{self.name=} {size=} {facing=}')
    else: 
      raise NotImplementedError(f'{self.name=} {size=}')
    if self.VERBOSE: print(f'{self.name=} {size=} {facing=} {x} {y} {w} {h}')
    #return rectgl
    return coords


  # TODO remove once Block.meander refactored
  def __guide(self, direction):
    ''' expand facing to a pair of guidelines for meander
    '''
    control = {
      'C': ('spiral', None), 
      'N': ('guided', 'EB', 'ET'),
      'S': ('guided', 'EB', 'ET'),
      'E': ('guided', 'SL', 'SR'),
      'W': ('guided', 'NL', 'NR')
    }
    if direction in control: return control[direction]
    else: # abandon if there are no guidelines defined
      raise KeyError(f'all at sea > {direction=} {self.name=} not found')

'''
the
end
'''
