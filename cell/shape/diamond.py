from shapely.geometry import Polygon, LineString, MultiLineString
from cell.meander import Line

class Diamond(Line):

  VERBOSE = False
  def __init__(self):
    self.name = 'diamond'

  def validate(self, geom):
    if geom['size'] in ['large', 'small']: 
      return 'wrong size'

  def guide(self, facing): return ('border', None)

  def paint(self, points, geom):
    ''' return polygon
    '''
    facing = geom['facing']
    coords = self.coords(points, facing)
    return Polygon(coords)

  def coords(self, points, facing):
    ''' extract points according to facing
        return tuples for Shapely
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    rings  = {
          'C': (w, n, e, s),
          'W': (w, n, s),
          'E': (n, e, s),
          'N': (w, n, e),
          'S': (w, e, s)
    }
    if facing in rings:
      return rings[facing]
    else:
      raise IndexError(f"Cannot face diamond {facing}")

  def draw(self, points, geom):
    #guideln = self.guidelines(points, geom)
    guideln = self.guidelnTriangle(points, geom, shape='diamond')
    points  = self.collectPoints(guideln)
    linstr  = self.makeStripes(points)
    return linstr

  '''
  def guidelines(self, points, geom):
    t = Triangle()
    return t.guideline(points, geom)

  def zz():
       B
     /   \
    A     C
     \   /
       D

    meander cannot handle odd cell length
    brute force to even length by reduction
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    facing = geom['facing']

    oddlen  = False
    if clen % 2:
      clen  -= 1
      oddlen = True
    x0 = y0 = 0
    x1 = y1 = clen / 2
    x2 = y2 = clen
    if oddlen:
      self.shape = Polygon([(x0, y1), (x1, y0), (x2, y1), (x1, y2)])
      print(f'{clen=} {facing=} {x0=} {x1=} {x2=} {y0=} {y1=} {y2=}')
    AB      = LineString([(x0,y1), (x1,y2)])
    AD      = LineString([(x0,y1), (x1,y0)])
    BC      = LineString([(x1,y2), (x2,y1)])
    CB      = LineString([(x2,y1), (x1,y2)])
    CD      = LineString([(x2,y1), (x1,y0)])
    DC      = LineString([(x1,y0), (x2,y1)])
    mls     = {
      'N': [AB, CB],
      'E': [BC, DC],
      'S': [AD, CD],
      'W': [AB, AD],
      'C': [BC, AD]
    }
    if facing in mls: 
      return MultiLineString(mls[facing])
    else: 
      raise IndexError(f'{facing} is unknown')
  '''
'''
the
end
'''

