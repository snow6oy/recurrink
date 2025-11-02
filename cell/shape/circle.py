import math
from shapely.geometry import Point, MultiLineString, LineString
from shapely import set_precision


class Circle:
  ''' circle plots badly (square wheels!) as Shape.draw()
      sets precision to whole number
      but aside from testing, it matters not as 
      the SVG output is smooth
  '''
  def __init__(self):
    self.name = 'circle'

  def validate(self, geom):
    if geom['facing'] != 'C': return 'must face all'

  # TODO transform across block
  def draw(self, points, geom):
    ''' line for meander
        uses Shapely.intersection to extract line part inside circle
    '''
    size   = geom['size']
    points = self.adjustSize(size, points)
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points

    radius = self.getRadius(size, clen, swidth)
    x, y   = mid
    circle = Point(x, y).buffer(radius)
    X, Y   = sw
    W, H   = ne
    points = list()
    points.append(Point(w))
    #print(f'{clen=} {mid=} {ne=} {sw=} {X=} {Y=} {W=} {H=}')

    for i in range(X, W):
      tail = Point([i, Y])
      top  = Point([i, H])
      tall = LineString([tail, top])
      trim = tall.intersection(circle)
      if len(trim.boundary.geoms) == 2:
        p1, p2 = trim.boundary.geoms  # pair of points
        if i % 2:
          points.append(p1)
          points.append(p2)
        else:
          points.append(p2)
          points.append(p1)
    points.append(Point(e))
    return LineString(points)

  def paint(self, points, geom):
    ''' returns a Polygon
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    size   = geom['size']
    radius = self.getRadius(size, clen, swidth)
    if radius:
      self.radius = int(radius)  # for drawing
      x, y   = mid
      circle = Point(x, y).buffer(radius)
      return set_precision(circle, grid_size=.1)
    else:
      raise IndexError(f"Cannot set circle to {size} size")

  def getRadius(self, size, clen, swidth):
    ''' pythagoras was a pythonista :)
    '''
    large         = clen / 2
    sum_two_sides = (large**2 + large**2)
    sizes         = {
       'large': (math.sqrt(sum_two_sides) - swidth),
      'medium': (clen / 2 - swidth),
       'small': (clen / 3 - swidth)
    }
    if size in sizes:
      radius = sizes[size]
      return int(radius)
  
  def adjustSize(self, size, points):
    ''' only bother to adjust e w sw ne as no other points are used by circle
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    offset = int(clen / 6)
    sizes  = {
      'small': [offset, int(clen - offset)],
      'large': [int(offset * -1), int(clen + offset)]
    }
    if size in sizes:
      mn, mx = sizes[size]   # offset
      w      = tuple([mn, w[1]]) 
      e      = tuple([mx, e[1]])
      sw     = tuple([mn, mn])
      ne     = tuple([mx, mx])
    points   = swidth, clen, n, e, s, w, ne, se, nw, sw, mid 
    # print(f'{w=} {sw=} {ne=} {clen=}')
    return points

  def drawConcentric(self, points, geom):
    ''' make rings for meander
        but despite elegance too hard to integrate
        so not used :/
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    size   = geom['size']
    x, y   = mid
    rings  = list()
    radius = self.getRadius(size, clen, swidth)

    for r in range(radius, 0, -2):
      c = Point(x, y).buffer(r)
      rings.append(c.boundary)
    return MultiLineString(rings)

'''
the
end
'''

