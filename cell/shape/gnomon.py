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

  def coords(self, x, y, clen, kwargs):
    ''' define the input to create Shapely Polygon
    '''
    X = x * clen
    Y = y * clen
    W = X + clen
    H = Y + clen
    a = Y + (clen / 3)  # x
    b = W - (clen / 3)  
    c = H - (clen / 3)  # h
    d = X + (clen / 3)
    facing = kwargs['facing']
    direction = {
      'north': [(X, Y), (X, H), (W, H), (W, c), (a, c), (a, Y)],
       'west': [(X, Y), (X, H), (a, H), (a, d), (W, d), (W, H)],
      'south': [(X, Y), (X, d), (b, d), (b, H), (W, H), (W, Y)],
       'east': [(X, c), (X, H), (W, H), (W, Y), (b, Y), (b, c)]
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
