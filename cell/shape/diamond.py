from shapely.geometry import Polygon, LineString, MultiLineString
from cell.meander import Line

class Diamond(Line):

  VERBOSE = False
  def __init__(self):
    self.name = 'diamond'

  def validate(self, geom):
    if geom['size'] in ['large', 'small']: 
      return 'wrong size'

  def draw(self, points, geom):
    guideln = self.guidelines(points, geom)
    points  = self.collectPoints(guideln)
    linstr  = self.makeStripes(points)
    return linstr

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


  # TODO avoid the cell length has to be even bug
  def guidelines(self, points, geom):
    '''  e - B - f
         |       |
         A       C
         |       |
         h - D - g 

         diamonds only know ABCD
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    if clen % 2: # odd length cannot meander
      raise ValueError(f'{clen} is odd')
    facing = geom['facing']
    bounds = [sw[0], sw[1], ne[0], ne[1]]

    AB   = LineString([w,  n])
    AD   = LineString([w,  s])
    BC   = LineString([n,  e])
    CB   = LineString([e,  n])
    CD   = LineString([e,  s])
    DC   = LineString([s,  e])

    mls  = {
      'N': [AB, CB],
      'E': [BC, DC],
      'S': [AD, CD],
      'W': [AB, AD],
      'C': [BC, AD]
    }
    if self.VERBOSE: print(f'{facing=} {mls[facing]}')
    if facing in mls: 
      return MultiLineString(mls[facing])
    else: 
      raise IndexError(f'{facing=} is unknown')

  def __guide(self, facing): return ('border', None)
'''
the
end
'''
