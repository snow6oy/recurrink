import matplotlib.pyplot as plt
import pprint
from shapely import line_merge # set_precision
from shapely.geometry import Polygon, LineString, MultiLineString, Point, LinearRing
pp = pprint.PrettyPrinter(indent=2)

class Meander:
  def __init__(self, polygon):
    if isinstance(polygon, list):
      raise TypeError(polygon)
    elif polygon.is_valid:
      self.shape = Polygon(polygon) # only a valid Shapely polygon can be used to Meander

  # TODO migrate consumers to Geomaker().padBlock
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
    err        = None
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
        err = f"{i=} {len(points[i])} points is not the same {same} "
        break
      same = len(points[i])
    return points, err

  def makeStripes(self, points):
    ''' sort the points into parallel stripes that join at alternate ends
        points is a two dim array each dim has 0..n length
        the first dim represents an axis and the second contains points along the axis
        an axis is paired with the next axis in sequence e.g. 0,1 1,2 2,3 
        paired stripes are molded into a continuous line by alternating based on odd/even
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

'''
the
end
'''
