from shapely.geometry import Polygon, LineString, MultiLineString
from cell.meander import Line

# TODO inherit from Meander and return a polyln
class Triangle(Line):
  ''' a linear ring wrapped in a Polygon 
      the wrapper is needed by transform
  '''
  VERBOSE = False

  def __init__(self):
    self.name = 'triangl' # misspelt due to 7char limit when CSV

  def paint(self, points, geom):
    ''' public wrapper of coords
        returns Shapely object
    '''
    facing = geom['facing']
    coords = self.coords(points, facing)
    return Polygon(coords)

  def coords(self, points, facing):
    ''' extract tuples from points and facing
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    rings = {
      'N': (nw, ne, s),
      'S': (sw, n, se),
      'E': (nw, e, sw),
      'W': (w, ne, se)
    }
    if facing in rings: return rings[facing]
    else: raise IndexError(f"Cannot face triangle {facing}")

  def draw(self, points, geom):
    guideln = self.guidelines(points, geom)
    points  = self.collectPoints(guideln)
    if len(points[0]) == len(points[1]):
       polyln = self.makeStripes(points)
    else:
      raise ValueError(f'Ouch! {self.pp.pprint(points)}')
    return polyln

  def validate(self, geom):
    if geom['facing'] == 'C':
      return 'cannot face Centre'
    if geom['size'] in ['small', 'large']:
      return 'wrong size'

  def guidelines(self, points, geom):
    '''  E - B - F
         |       |
         A       C
         |       |
         H - D - G 
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    if clen % 2: # odd length cannot meander
      raise ValueError(f'{clen} is odd')
    facing = geom['facing']
    bounds = [sw[0], sw[1], ne[0], ne[1]]

    ED   = LineString([nw, s])
    FD   = LineString([ne, s])
    HB   = LineString([sw, n])
    GB   = LineString([se, n])
    EC   = LineString([nw, e])
    HC   = LineString([sw, e])
    AF   = LineString([w, ne])
    AG   = LineString([w, se])
    BC   = LineString([n,  e])
    AD   = LineString([w,  s])
    mls  = {
      'N': [HB, GB],
      'S': [ED, FD],
      'E': [EC, HC],
      'W': [AF, AG]
    }
    if self.VERBOSE: print(f'{facing=} {mls[facing]}')
    if facing in mls: 
      return MultiLineString(mls[facing])
    else: 
      raise IndexError(f'{facing=} is unknown')

  def __guide(self, facing): return ('selfsvc', None)
'''
the
end
'''
