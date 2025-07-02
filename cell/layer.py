from shapely.geometry import Polygon, LineString
from .shape import *

class Layer:

  VERBOSE = False

  def __init__(self, pos=tuple([0,0]), clen=60): 
    self.bft       = list()
    self.direction = list()   # make guide for meander
    self.clen      = clen     # length of cell
    self.pos       = pos      # logical position in block

  def background(self): 
    X, Y, W, H, *a = self.dimension(self.pos[0], self.pos[1], self.clen)
    self.bft.append(((X, Y), (X, H), (W, H), (W, Y)))
    self.direction.append(('EB','ET'))

  def foreground(self, **kwargs):
    ''' Block.walk also calls here when top
    '''
    name   = kwargs['shape'] if 'shape' in kwargs else 'square'
    shapes = {
      'line': Rectangle(name),
      'square': Rectangle(name),
      'gnomon': Gnomon()
    }
    dim     = self.dimension(self.pos[0], self.pos[1], self.clen)
    shape   = shapes[name]
    coords  = shape.coords(dim, kwargs)
    if len(coords): self.bft.append(coords)
    self.direction.append(shape.guide(kwargs['facing']))

  def polygon(self):
    if len(self.bft) == 3:
      p = Polygon(self.bft[0], holes=[self.bft[1], self.bft[2]])
    else:             # must be two right ?
      p = Polygon(self.bft[0], holes=[self.bft[1]])
    return p

  def dimension(self, x, y, clen):
    ''' set dimensions for all shapes 

    usage examples

    1. unpack everything
    X, Y, W, H, a, b, c, d, A, B, C, D = dim

    2. unpack for medium sized shape
    X, Y, W, H, *a = dim
       
        o---------o D
        | +.....+ | H
        | . x x . | d
        | . x x . | b
        | +.....+ | Y
        o---------o B 
        A X a c W C
    '''
    X = x * clen              # medium
    Y = y * clen
    W = X + clen
    H = Y + clen
    a = X + (clen / 3)        # small
    b = Y + (clen / 3)
    c = W - (clen / 3)
    d = H - (clen / 3)
    A = X + (clen / 3) * 4    # large
    B = X + (clen / 3) * 4
    C = Y + (clen / 3) * 2
    D = Y + (clen / 3) * 2

    return tuple([X, Y, W, H, a, b, c, d, A, B, C, D])

'''
the
end
'''
