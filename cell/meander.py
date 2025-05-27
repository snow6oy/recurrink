import math
import matplotlib.pyplot as plt
import pprint
from shapely import line_merge, set_precision
from shapely.geometry import (
  Polygon, LineString, MultiLineString, Point, LinearRing
)
pp = pprint.PrettyPrinter(indent=2)

class Spiral:
  '''
  1 2 3     
  8 9 4
  7 6 5

   1  2  3  4
  12 13 14  5
  11 16 15  6
  10  9  8  7

   1  2  3  4  5      1  2  3  4  5  6
  16 17 18 19  6     20 21 22 23 24  7
  15 24 25 20  7     19 32 33 34 25  8
  14 23 22 21  8     18 31 36 35 26  9
  13 12 11 10  9     17 30 29 28 27 10
                     16 15 14 13 12 11
  '''
  VERBOSE = False

  def spiral(self, clen):
    ''' split a LineString and return a MultiLineString
        split on boundary of Polygon.interiors[0]
    '''
    if len(self.shape.interiors) != 1: raise IndexError()
    if self.shape.interiors[0].geom_type != 'LinearRing':
      raise ValueError()
    line   = self.matrix(clen)
    hole   = self.shape.interiors[0]
    mls    = self.splitLines(line, Polygon(hole))
    return MultiLineString(mls) 

  def splitLines(self, line, hole):
    ''' test line using touches and contains 
        split when spiral passes inside hole
    '''
    inside = False
    mls = []
    new_line = []
    for xy in line:
      pt = Point(xy)
      #print(f"{hole.touches(pt)=} {inside=} {xy}")
      if hole.touches(pt) and inside: pass
      elif hole.touches(pt):
        new_line.append(xy)
        if hole.contains(LineString(new_line)): 
          inside  = True
        else:
          mls.append(LineString(new_line))
          inside  = True
      elif inside:
        new_line = []
        new_line.append(xy)
        inside   = False
      else:
        new_line.append(xy)
    return MultiLineString(mls)

  def matrix(self, LEN):
    ''' call rows 1, 2 and col 1, 2 and pack points into a list
    '''
    count = 0  # final number of cells
    n = 0      # depth of spiral
    db = {}    # temp data collection
    m = [[0]*LEN for i in range(LEN)] # output template

    for n in range(LEN):
      db = {**db, **self.r1(count, n, LEN)} # append top rows
      count = max(db.keys())           # track last item
      if (count == LEN * LEN): break   # are we there yet?

      db = {**db, **self.c1(count, n, LEN)} # right hand cols
      count = max(db.keys())

      db = {**db, **self.r2(count, n, LEN)} # bottom rows
      count = max(db.keys())
      if (count >= LEN * LEN): break

      db = {**db, **self.c2(count, n, LEN)} # left hand col
      count = max(db.keys())

    if self.VERBOSE:
      for k in db:   # convert to printer friendly format
        r = db[k][0]
        c = db[k][1]
        m[r][c] = f"{k:02d}"
        [print(" ".join(s)) for s in m]
    return list(db.values())

  def r1(self, s, n, l):
    ''' x x x 
        o o o
        o o o 
    n+1 to LEN-n '''
    line = {}
    A = x = n
    B = l - n
    if self.VERBOSE: print("A={} B={} x={} END={}".format(A, B, x, (l * l))) 

    for y in range(A, B):
      s += 1 
      if s > (l * l): break
      if self.VERBOSE: print("r1 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def c1(self, s, n, l):
    ''' o o o
        o o x
        o o o
    n+1 to LEN-n '''
    line = {}
    A = n + 1
    B = l - n
    y = l - n - 1
    if self.VERBOSE: print("A={} B={} y={}".format(A, B, y)) 
    for x in range(A, B):
      s += 1 
      if s > (l * l): break
      if self.VERBOSE: print("c1 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def r2(self, s, n, l):
    ''' o o o
        o o o
        x x x 
    LEN-n+1 to n '''
    line = {}
    A = l - (n + 2)
    x = l - (n + 1)
    B = n - 1
    if self.VERBOSE: print("A={} B={} x={}".format(A, B, x)) 
    for y in range(A, B, -1):  # 1, -1
      s += 1
      if s > (l * l): break
      if self.VERBOSE: print("r2 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def c2(self, s, n, l):
    ''' o o o
        x o o
        o o o
    LEN-n+1 to n '''
    line = {}
    A = l - (n + 2)
    y = n
    B = n
    if self.VERBOSE: print("A={} B={} y={}".format(A, B, y)) 
    for x in range(A, B, -1):
      s += 1
      if self.VERBOSE: print("c2 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

class Meander(Spiral):
  ''' a valid Shapely polygon is required to Meander
  '''
  VERBOSE = False

  def __init__(self, polygon):
    if isinstance(polygon, list):
      raise TypeError(polygon)
    elif polygon.is_valid:
      precise = set_precision(polygon, grid_size=1)
      self.shape = precise #  Polygon(polygon) 

  # TODO migrate consumers to Geomaker().padBlock
  # Migration on hold due to testing issue
  def pad(self):
    ''' make a gap between cells by adding padding with Shapely.buffer
        a small Polygon may end up empty. Then silently return the original
        Shapely.set_precision did not help
    '''
    b = self.shape.buffer(-1, single_sided=True)
    return self.shape if b.is_empty else b

  def guidelines(self, padme, direction):
    '''
    NW  N  NE      WT ET
      ↖ ↑ ↗     NL +---+ NR
    W ←   → E      |   | 
      ↙ ↓ ↘     SL +---+ SR
    SW  S  SE      WB EB
    '''
    x, y, w, h = padme.bounds
    '''
    ibounds    = [int(x) for x in padme.bounds] # convert to int to match grid
    x, y, w, h = ibounds
    if not (w - x) == (h -y):
      raise ValueError(f"{(w - x)} and {h -y} became inequal")
    '''
    mls        = []
    guideline  = {
      'NL': LineString([(x, y), (x, h)]), # North Left
      'NE': LineString([(x, y), (w, h)]), # North East
      'EB': LineString([(x, y), (w, y)]), # East Bottom
      'SE': LineString([(x, h), (w, y)]), # South East
      'SL': LineString([(x, h), (x, y)]), # South Left
      'SW': LineString([(w, h), (x, y)]), # South West
      'WB': LineString([(w, y), (x, y)]), # West Bottom
      'NW': LineString([(w, y), (x, h)]), # North West
      'NR': LineString([(w, y), (w, h)]), # North Right
      'ET': LineString([(x, h), (w, h)]), # East Top
      'SR': LineString([(w, h), (w, y)]), # South Right
      'WT': LineString([(w, h), (x, h)])  # West Top
    }
    [mls.append(guideline[d]) for d in direction]
    return MultiLineString(mls) 

  def collectPoints(self, padme, guidelines):
    ''' collect the points intersecting the padded version of shape
        gridwalk the bounding box and collect Points() touching the guidelines
        grouped by the guidelines
    '''
    points     = []
    same       = 0
    for i, gl in enumerate(list(guidelines.geoms)):
      points.append([]) # template
      start_x, stop_x, step_x, start_y, stop_y, step_y = self.orderGrid(gl)
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          if padme.covers(pt):      # surface test for gnomons
            if gl.intersects(pt):   # collect the points on the guideline
              points[i].append((x,y))
      ''' uneven polygons generate guidelines that cannot go around corners
          the following condition tests whether point collecting can succeed
      '''
      if i > 0 and len(points[i]) is not same:
        prev = i-1
        raise IndexError(f"""
{i=} {len(points[i])} points is not the same {same}
this guideline
{list(guidelines.geoms)[prev]}
{points[prev]}
prev guideline
{list(guidelines.geoms)[i]}
{points[i]}
""")
      same = len(points[i])
    return points

  def makeStripes(self, points):
    ''' sort the points into parallel stripes that join at alternate ends
        points is a two dim array each dim has 0..n length
        the first dim represents an axis and the 
        second contains points along the axis
        an axis is paired with the next axis in sequence e.g. 0,1 1,2 2,3 
        paired stripes are molded into a continuous line by 
        alternating based on odd/even
        pp.pprint(points)
    '''
    #points = [list('afg'), list('beh'), list('cdi')]
    sorted_points = []
    for i in range(len(points[0])):
      stripe = [j[i] for j in reversed(points)] if i % 2 else [j[i] for j in points]
      [sorted_points.append(s) for s in stripe]
    #pp.pprint(sorted_points)
    return LineString(sorted_points)

  def joinStripes(self, p1, p2):
    ''' orchestrate make stripes calls and join two points
    '''
    s1       = self.makeStripes(p1)
    last_p1  = list(s1.coords)[-1] # sort the points before marking the last
    s2       = self.makeStripes(p2)
    s2       = list(s2.coords)      # extract list from LineString 
    s2       = list(reversed(s2))   # 
    first_p2 = s2[0]
    s2.insert(0, last_p1)           # guess that last p1 matches first p2
    s2       = LineString(s2)
    mls      = MultiLineString([s1, s2])

    stripe  = line_merge(mls)
    if stripe.geom_type != 'LineString':
      raise TypeError(f"""
line merge failed {stripe.geom_type} is wrong type. Check {last_p1=} {first_p2=}
""")
    return stripe

  def orderGrid(self, guideline):
    ''' private method to simplify collectPoints()
        calculate the grid order by converting LineString
        into parameters for iteration
    '''
    start, stop      = list(guideline.coords)
    start_x, start_y = [int(xy) for xy in start]
    stop_x, stop_y   = [int(xy) for xy in stop]
    step_x           = -1 if start_x > stop_x else 1
    step_y           = -1 if start_y > stop_y else 1
    stop_x          += step_x
    stop_y          += step_y
    return start_x, stop_x, step_x, start_y, stop_y, step_y

  def ___checkGuide(self, guidelines):
    ''' who calls here ? use plotGuideline
    '''
    err        = None
    same       = 0
    for i, gl in enumerate(list(guidelines.geoms)):
      start_x, stop_x, step_x, start_y, stop_y, step_y = self.orderGrid(gl)
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          t  = ' '
          if padme.covers(pt):      # surface test for gnomons
            if gl.intersects(pt):   # collect the points on the guideline
              points[i].append((x,y))
      if i > 0 and len(points[i]) is not same:
        err = f"{i} {direction[i]=} {len(points[i])} points is not the same {same} "
        break
      same = len(points[i])
    return points, err

  def setClock(self, width, height):
    ''' meandering an odd number of stripes requires 
     direction order to be clockwise
     even stripes must be anti-clockwise
  
     tests suggest that when num of stripes is 1 then 
     clockwise should be True
     ignoring that corner case for now ..
    '''
    raw_stripes   = (width - 1) / 3         # padding reduces width
    numof_stripes = math.floor(raw_stripes) # round down
    clockwise     = False if numof_stripes % 2 else True
    return clockwise

'''
the
end
'''
