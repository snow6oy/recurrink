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
      'S': (nw, ne, s),
      'N': (sw, n, se),
      'E': (nw, e, sw),
      'W': (w, ne, se)
    }
    if facing in rings: return rings[facing]
    else: raise KeyError(f"Cannot face triangle {facing}")

  def draw(self, points, geom):
    guideln = self.guidelines(points, geom)
    twoside = self.collectPoints(guideln, facing=geom['facing'])
    points  = [twoside[0] + twoside[1], twoside[2]]
    #self.pp.pprint(points)
    if len(points[0]) == len(points[1]):
       polyln = self.makeStripes(points)
    else:
      raise ValueError(f'Ouch! {self.pp.pprint(points)}')
    return polyln

  def orderGrid(self, guideline, facing=None):
    ''' private method to simplify collectPoints()
        calculate the grid order by converting LineString
        into parameters for iteration
    '''
    start, stop      = list(guideline.coords)
    start_x, start_y = [int(xy) for xy in start]
    stop_x, stop_y   = [int(xy) for xy in stop]
    step_x           = -1 if start_x > stop_x else 1
    step_y           = -1 if start_y > stop_y else 1
    if facing in ['E', 'W']: stop_x += step_x
    else:                    stop_y += step_y
    return start_x, stop_x, step_x, start_y, stop_y, step_y

  def _orderGrid(self, guideln):
    #print('hi', list(guideln.coords))
    if guideln.coords[0] == (1, 1): return [1, 18, 1, 1, 18, 1]
    else: return [1, 18, 1, 16, 1, -1]

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

    HB   = LineString([sw,  n])
    BG   = LineString([n,  se])
    HG   = LineString([sw, se])
    ED   = LineString([nw,  s])
    DF   = LineString([s,  ne])
    EF   = LineString([nw, ne])

    HE   = LineString([sw, nw])
    CE   = LineString([e,  nw])
    HC   = LineString([sw,  e])

    FA   = LineString([ne,  w])
    AG   = LineString([w,  se])
    FG   = LineString([ne, se])
    mls  = {
      'N': [HB, BG, HG],
      'S': [ED, DF, EF],
      'E': [HC, CE, HE],
      'W': [FA, AG, FG]
    }
    '''
    BC   = LineString([n,   e])
    AD   = LineString([w,   s])
    HC   = LineString([sw,  e])
    GB   = LineString([se,  n])
    'N': [HB, GB], 'S': [ED, FD], 'E': [EC, HC], 'W': [AF, AG]
    '''
    if self.VERBOSE: print(f'{facing=} {mls[facing]}')
    if facing in mls: 
      return MultiLineString(mls[facing])
    else: 
      raise KeyError(f'{facing=} is unknown')
'''
the
end
'''
