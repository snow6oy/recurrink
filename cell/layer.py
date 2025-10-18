from shapely.geometry import (
  Polygon, LineString, MultiPolygon, Point, MultiLineString
)
from .shape import *

class Layer:

  VERBOSE = False

  # TODO expose padding so Block.walk() can init
  def __init__(self, pos=tuple([0,0]), clen=9, linear=False): 
    self.bft       = list()
    #self.direction = list()   # make guide for meander
    self.clen      = clen     # length of cell
    self.pos       = pos      # logical position in block
    self.linear    = linear   # use draw instead of paint

  def background(self, cell): 
    if self.linear:
      x, y = self.pos
      dim  = self.dimension(x, y, self.clen)
      size = cell['geom']['size']
      if cell['color']['background'] is None:
        drawn = LineString()
      elif cell['geom']['name'] == 'sqring':
        ''' square rings have outer ring as bg
            others swap direction depending whether odd or even
        '''
        spiral = Rectangle('spiral')
        drawn  = spiral.draw(self.clen, dim, geom)
      elif x % 2: 
        square = Rectangle('square')
        drawn  = square.draw(self.clen, dim, {'facing': 'N', 'size': 'medium'})
      else: 
        square = Rectangle('square')
        drawn  = square.draw(self.clen, dim, {'facing': 'E', 'size': 'medium'})
      #if drawn: 
      self.bft.append(drawn)
    else:
      X, Y, W, H, *a = self.dimension(self.pos[0], self.pos[1], self.clen)
      self.bft.append(Polygon(((X, Y), (X, H), (W, H), (W, Y))))

  def foreground(self, geom):
    ''' Block.walk also calls here when top
    '''
    if 'stroke_width' in geom: sw = geom['stroke_width']
    else: sw = 0
    name   = geom['name'] if 'name' in geom else 'square'
    x, y   = self.pos
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
    points = self.points(x, y, sw, self.clen)
    dim    = self.dimension(x, y, self.clen)

    if self.linear and name in ['triangl', 'circle', 'diamond']:
      z = shape.draw(points, geom) 
    elif name in ['triangl', 'circle', 'diamond']:
      z = shape.paint(points, geom)
    elif self.linear:
      z = shape.draw(self.clen, dim, geom)
    else:
      z = shape.paint(dim, geom)
    if z.geom_type: self.bft.append(z)

  def dimension(self, x, y, clen):
    ''' set dimensions for all rectangular shapes 

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
    scaler = clen / 3    # scale up or down by a factor of three

    X = x * clen         # medium
    Y = y * clen
    W = X + clen
    H = Y + clen
    a = X + scaler       # small
    b = Y + scaler
    c = W - scaler
    d = H - scaler
    A = X - scaler       # large
    B = Y - scaler
    C = W + scaler
    D = H + scaler

    return tuple([X, Y, W, H, a, b, c, d, A, B, C, D])

  def points(self, x, y, stroke_width, clen):
    X = x * clen
    Y = y * clen

    swd = stroke_width
    cl  = clen
    s   = tuple([X + cl / 2,   Y + swd])
    e   = tuple([X + cl - swd, Y + cl / 2])
    n   = tuple([X + cl / 2,   Y + cl - swd])
    w   = tuple([X + swd,      Y + cl / 2])
    ne  = tuple([X + cl - swd, Y + cl - swd])
    se  = tuple([X + cl - swd, Y + swd] )
    nw  = tuple([X + swd,      Y + cl - swd])
    sw  = tuple([X + swd,      Y + swd])
    mid = tuple([X + cl / 2,   Y + cl / 2])

    return tuple([swd, cl, n, e, s, w, ne, se, nw, sw, mid])

'''
the
end
'''
