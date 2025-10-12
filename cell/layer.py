import math
from shapely.geometry import Polygon, LineString, MultiPolygon, Point
from .shape import *

class Layer:

  VERBOSE = False

  # TODO expose padding so Block.walk() can init
  def __init__(self, pos=tuple([0,0]), clen=9, linear=False): 
    self.bft       = list()
    self.direction = list()   # make guide for meander
    self.clen      = clen     # length of cell
    self.pos       = pos      # logical position in block
    self.linear    = linear   # use draw instead of paint

  def background(self, cell): 
    X, Y, W, H, *a = self.dimension(self.pos[0], self.pos[1], self.clen)
    geom  = cell['geom']
    empty = cell['color']['background'] is None
    ''' square rings have outer ring as bg
        others swap direction depending whether odd or even
    '''
    if empty:
      self.direction.append((None, None))
    else:
      if geom['name'] == 'sqring':
        self.direction.append(('spiral', None)) # override Rectangle
      elif self.pos[0] % 2: self.direction.append(('guided', 'EB','ET'))
      else: self.direction.append(('guided', 'NL','NR'))
    self.bft.append(Polygon(((X, Y), (X, H), (W, H), (W, Y))))

  def foreground(self, geom):
    ''' Block.walk also calls here when top
    '''
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
    shape   = shapes[name]
    if 'stroke_width' in geom: sw  = geom['stroke_width']
    else: sw = 0
    if name in ['triangl', 'circle', 'diamond']:
      dim = points = self.points(x, y, sw, self.clen)
      drawn = shape.draw(points, geom)
      #print(f'  {drawn.geom_type}')
      self.direction.append(['selfsvc', drawn])
    elif name in ['gnomon', 'parabol']:
      dim = self.dimension(x, y, self.clen)
      drawn = shape.draw(self.clen, dim, geom)
      #print(f'  {drawn.geom_type}')
      self.direction.append(['selfsvc', drawn])
    else:
      dim = self.dimension(x, y, self.clen)
      drawn = shape.draw(self.clen, dim, geom)
      self.direction.append(['selfsvc', drawn])
      '''
      print(f'  {drawn.geom_type}')
      dim = self.dimension(x, y, self.clen)
      self.direction.append(shape.guide(geom['facing']))
      '''

    if name in ['line','edge','square','sqring']:
      polygn = shape.paint(dim, geom)
    else:
      polygn = shape.coords(dim,geom)
    if polygn.geom_type: self.bft.append(polygn)

  def polygon(self):
    return MultiPolygon(self.bft)

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

  def __points(self, x, y, stroke_width, clen):
    X = x * clen
    Y = y * clen

    swd = stroke_width
    cl  = clen
    n   = tuple([X + cl / 2,   Y + swd])
    e   = tuple([X + cl - swd, Y + cl / 2])
    s   = tuple([X + cl / 2,   Y + cl - swd])
    w   = tuple([X + swd,      Y + cl / 2])
    ne  = tuple([X + cl - swd, Y + swd] )
    se  = tuple([X + cl - swd, Y + cl - swd])
    nw  = tuple([X + swd,      Y + swd])
    sw  = tuple([X + swd,      Y + cl - swd])
    mid = tuple([X + cl / 2,   Y + cl / 2])

    return tuple([swd, cl, n, e, s, w, ne, se, nw, sw, mid])


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
    #print(f'{numof_stripes=}')
    return False if numof_stripes % 2 else True

'''
the
end
'''
