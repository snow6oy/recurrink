import math
import matplotlib.pyplot as plt
import pprint
from shapely import line_merge # set_precision
from shapely import Polygon, LineString, MultiLineString, Point, LinearRing
pp = pprint.PrettyPrinter(indent=2)

class Meander:
  ''' a valid Shapely polygon is required to Meander
  '''
  VERBOSE = False

  def __init__(self, polygon):
    if isinstance(polygon, list):
      raise TypeError(polygon)
    elif polygon.is_valid:
      self.shape = Polygon(polygon) 

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
      #if self.VERBOSE: print(f"{i} {gl=}")
      points.append([]) # template
      start_x, stop_x, step_x, start_y, stop_y, step_y = self.orderGrid(gl)
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          if padme.covers(pt):      # surface test for gnomons
            if self.VERBOSE: print(f"  {x} {y} ", flush=True, end='')
            if gl.intersects(pt):   # collect the points on the guideline
              points[i].append((x,y))
              if self.VERBOSE: print('*')
            if self.VERBOSE: print()
      ''' uneven polygons generate guidelines that cannot go around corners
          the following condition tests whether point collecting can succeed
      '''
      if i > 0 and len(points[i]) is not same:
        if self.VERBOSE:
          print(f"{i=} {len(points[i])} points is not the same {same}\n")
          prev = i-1
          print(err)
          print(list(guidelines.geoms)[prev])
          pp.pprint(points[prev])
          print(list(guidelines.geoms)[i])
          pp.pprint(points[i])
        break
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

  def checkGuide(self, guidelines):
    ''' who calls here ?
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
