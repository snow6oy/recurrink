from shapely.geometry import Polygon, LineString
from cell.meander import Line

class Gnomon(Line):
  ''' Gnomon has an area of IDGP that equals HPFB
    D  G  C
    I  P  F
    A  H  B
    https://en.wikipedia.org/wiki/Theorem_of_the_gnomon
  '''
  VERBOSE = False

  def __init__(self):
    self.name = 'gnomon'

  def validate(self, geom): 
    if geom['size'] in ['large', 'small']: 
      return 'strictly medium'

  def draw(self, clen, dim, geom):
    facing  = geom['facing']
    guideln = self.guidelines(facing, clen, dim[:4])
    points  = self.collectPoints(guideln)
    square  = self.makeStripes(points)
    points  = self.sliceByThird(facing, square.coords)
    return LineString(points)

  def paint(self, dim, kwargs):
    ''' wrapper around coords
    '''
    facing  = kwargs['facing']
    size    = kwargs['size']
    coords  = self.coords(dim, facing, size)
    return Polygon(coords)

  def coords(self, dim, facing, size):
    ''' define the input so Shapely Polygon can create an L shape

        +--+         +-           -+
        |  |  medium |     small   |
        +--+         +--+
    '''
    X, Y, W, H, a, b, c, d, *A = dim

    sizes   = {
      'medium': {
          'SW': [(X, Y), (X, H), (W, H), (W, d), (a, d), (a, Y)],
          'NW': [(X, Y), (X, H), (a, H), (a, b), (W, b), (W, Y)],
          'NE': [(X, Y), (X, b), (c, b), (c, H), (W, H), (W, Y)],
          'SE': [(X, d), (X, H), (W, H), (W, Y), (c, Y), (c, d)] 
       },
       'small': {
          'SW': [(X, b), (X, H), (c, H), (c, d), (a, d), (a, b)],
          'NW': [(X, Y), (X, d), (a, d), (a, b), (c, b), (c, Y)],
          'NE': [(a, Y), (a, b), (c, b), (c, d), (W, d), (W, Y)],
          'SE': [(a, d), (a, H), (W, H), (W, b), (c, b), (c, d)] 
       }
    }
    if size in sizes and facing in sizes[size]: 
      return sizes[size][facing]
    else: 
      raise IndexError(f"gnomon at sea {size} {facing}")

  def __guide(self, facing):
    ''' see Meander to check the codes 
    '''
    control = {
      'NW': ('guided', 'WB', 'NW', 'NR'),
      'SE': ('guided', 'SL', 'SE', 'ET'),
      'SW': ('guided', 'ET', 'NE', 'NR'),
      'NE': ('guided', 'WB', 'SW', 'SL')
    }
    ''' these guidelines throw exception in collectPoints
    '''
    if facing in control: return control[facing]
    else: raise KeyError(f'all at sea > {facing} <')

'''
the
end
'''
