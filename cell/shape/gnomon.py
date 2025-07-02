class Gnomon:
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

    facing    = kwargs['facing']
    direction = {
      'north': [(X, Y), (X, H), (W, H), (W, d), (b, d), (b, Y)],
       'west': [(X, Y), (X, H), (b, H), (b, a), (W, a), (W, H)],
      'south': [(X, Y), (X, a), (c, a), (c, H), (W, H), (W, Y)],
       'east': [(X, d), (X, H), (W, H), (W, Y), (c, Y), (c, d)]
    }
    if facing in direction: return direction[facing]
    else: raise IndexError(f"gnomon at sea {facing}")

  def guide(self, direction):
    ''' see Meander to check the codes 
    '''
    control = {
      'north': ('WB', 'NW', 'NR'),
      'south': ('SL', 'SE', 'ET')
    }
    if direction in control: return control[direction]
    else: raise KeyError(f'all at sea > {direction} <')

'''
the
end
'''
