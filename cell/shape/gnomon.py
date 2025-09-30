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

  def coords(self, dim, kwargs):
    ''' define the input so Shapely Polygon can create an L shape
    '''
    X, Y, W, H, a, b, c, d, *A = dim

    facing  = kwargs['facing']
    size    = kwargs['size']
    sizes   = {
      'medium': {
          'NW': [(X, Y), (X, H), (W, H), (W, d), (a, d), (a, Y)],
          'SW': [(X, Y), (X, H), (a, H), (a, b), (W, b), (W, Y)],
          'SE': [(X, Y), (X, b), (c, b), (c, H), (W, H), (W, Y)],
          'NE': [(X, d), (X, H), (W, H), (W, Y), (c, Y), (c, d)] 
       },
       'small': {
          'NW': [(X, b), (X, H), (c, H), (c, d), (a, d), (a, b)],
          'SW': [(X, Y), (X, d), (a, d), (a, b), (c, b), (c, Y)],
          'SE': [(a, Y), (a, b), (c, b), (c, d), (W, d), (W, Y)],
          'NE': [(a, d), (a, H), (W, H), (W, b), (c, b), (c, d)] 
       }
    }
    if size in sizes and facing in sizes[size]: 
      return Polygon(sizes[size][facing])
    else: raise IndexError(f"gnomon at sea {size} {facing}")

  def draw(self, clen, dim, geom):
    facing  = geom['facing']
    guideln = self.guidelines(facing, clen, dim[:4])
    points  = self.collectPoints(guideln)
    square  = self.makeDiagonals(points)
    # to make a gnomon slice by a third
    sqlen   = len(list(square.coords))
    if sqlen % 3: raise ValueError(f'Ouch! {sqlen} is not divisible by three')
    if facing == 'NW' or facing == 'SE':
      start   = int((sqlen / 3) * 2) - 1
      stop    = -1
    elif facing == 'SW' or facing == 'NE':
      start   = 0
      stop    = int(sqlen / 3) - 1
    points  = list(square.coords)[start:stop]
    return LineString(points)

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

  def validate(self, geom): 
    if geom['size'] in ['large', 'small']: 
      return 'strictly medium'


'''
the
end
'''
