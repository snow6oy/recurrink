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
      'north': [(X, Y), (X, H), (W, H), (W, d), (a, d), (a, Y)],
       'west': [(X, Y), (X, H), (a, H), (a, b), (W, b), (W, Y)],
      'south': [(X, Y), (X, b), (c, b), (c, H), (W, H), (W, Y)],
       'east': [(X, d), (X, H), (W, H), (W, Y), (c, Y), (c, d)] 
    }
    if facing in direction: return direction[facing]
    else: raise IndexError(f"gnomon at sea {facing}")

  def guide(self, direction):
    ''' see Meander to check the codes 
    '''
    control = {
      'north': ('WB', 'NW', 'NR'),
      'south': ('SL', 'SE', 'ET'),
       'east': ('NL', 'NE', 'SR'),
       'west': ('WT', 'SW', 'EB')
    }
    if direction in control: return control[direction]
    else: raise KeyError(f'all at sea > {direction} <')

'''
the
end
'''
