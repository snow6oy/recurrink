import math
from shapely.geometry import Polygon, LineString, MultiPolygon
from .shape import *

class Layer:

  VERBOSE = False

  # TODO expose padding so Block.walk() can init
  def __init__(self, pos=tuple([0,0]), clen=60): 
    self.bft       = list()
    self.direction = list()   # make guide for meander
    self.clen      = clen     # length of cell
    self.pos       = pos      # logical position in block

  def background(self): 
    X, Y, W, H, *a = self.dimension(self.pos[0], self.pos[1], self.clen)
    self.bft.append(((X, Y), (X, H), (W, H), (W, Y)))
    self.direction.append(('guided', 'EB','ET'))

  def foreground(self, **kwargs):
    ''' Block.walk also calls here when top
    '''
    name   = kwargs['shape'] if 'shape' in kwargs else 'square'
    shapes = {
         'line': Rectangle(name),
         'edge': Rectangle(name),
       'square': Rectangle(name),
       'sqring': Rectangle(name),
       'gnomon': Gnomon(),
      'parabol': Parabola()
    }
    dim     = self.dimension(self.pos[0], self.pos[1], self.clen)
    shape   = shapes[name]
    coords  = shape.coords(dim, kwargs)
    if len(coords): self.bft.append(coords)
    self.direction.append(shape.guide(kwargs['facing']))

  def polygon(self):
    ''' convert LinearRings in bft to one of the folllowing

        Polygon           1     background only
        Polygon + hole    1     square ring
        Polygon           2	background + foreground
        Polygon           3	bg fg + top
    '''
    polygons = list()

    if len(self.bft) == 1:       # bg only
      polygons.append(Polygon(self.bft[0]))
    elif len(self.bft) == 2:     # sqring or two polygns
      p = Polygon(self.bft[0], holes=[self.bft[1]])
      if p.is_valid: polygons.append(p)
      else: polygons = [Polygon(lring) for lring in self.bft]
    elif len(self.bft) == 3:     # top
      [polygons.append(Polygon(lring)) for lring in self.bft]

    for p in polygons:
      if p.is_valid: continue
      raise TypeError(p)
    
    return MultiPolygon(polygons) if len(polygons) else polygons[0]

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

  def setClock(self, padding=True):
    ''' position join point for composite meanders

     meandering an odd number of stripes requires 
     direction order to be clockwise
     even stripes must be anti-clockwise
  
     tests suggest that when num of stripes is 1 then 
     clockwise should be True
     ignoring that corner case for now ..

     ALSO ignoring this

    raw_stripes   = (width - 1) / 3         # padding reduces width
    '''
    clen          = self.clen =- 1 if padding else self.clen
    raw_stripes   = clen / 3
    numof_stripes = math.floor(raw_stripes) # round down
    return False if numof_stripes % 2 else True

'''
the
end
'''
