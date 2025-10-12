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

  def coords(self, points, geom):

    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    facing = geom['facing']
    rings = {
      'N': (nw, ne, s),
      'S': (sw, n, se),
      'E': (nw, e, sw),
      'W': (w, ne, se)
    }
    if facing in rings:
      return Polygon(rings[facing])
    else: raise IndexError(f"Cannot face triangle {facing}")

  def draw(self, points, geom):
    #guideln = self.guideline(points, geom)
    guideln = self.guidelnTriangle(points, geom, shape='triangle')
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

  def guide(self, facing): return ('selfsvc', None)

  # TODO avoid the cell length has to be even bug
  def guideline(self, points, geom):
    '''
    nw- n -ne
    |       |
    w       e
    |       |
    sw- s -se
    '''
    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    if clen % 2: # odd length cannot meander
      raise ValueError(f'{clen} is odd')
    facing = geom['facing']

    nw_s = LineString([nw, s])
    ne_s = LineString([ne, s])
    sw_n = LineString([sw, n])
    se_n = LineString([se, n])
    nw_e = LineString([nw, e])
    sw_e = LineString([sw, e])
    w_ne = LineString([w, ne])
    w_se = LineString([w, se])
    n_e  = LineString([n,  e])
    w_s  = LineString([w,  s])
    mls  = {
      'N': [sw_n, se_n],
      'S': [nw_s, ne_s],
      'E': [nw_e, sw_e],
      'W': [w_ne, w_se],
      'C': [n_e,   w_s]
    }
    if self.VERBOSE: print(f'{facing=} {mls[facing]}')
    if facing in mls: return MultiLineString(mls[facing])
    else: raise IndexError(f'{facing} is unknown')

'''
the
end
'''
