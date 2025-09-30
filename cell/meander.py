import pprint
from shapely.geometry import Point, LineString, MultiLineString

class Line:
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)

  def __guidelines(self, direction, shape=None):
    '''
    NW  N  NE      WT ET
      ↖ ↑ ↗     NL +---+ NR
    W ←   → E      |   | 
      ↙ ↓ ↘     SL +---+ SR
    SW  S  SE      WB EB
    '''
    padme      = shape if shape else self.shape
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

  def guidelines(self, facing, clen, bounds):
    '''  E - B - F
         |       |
         A       C
         |       |
         H - D - G 
    '''
    x, y, w, h = bounds  # X,Y because Shapely Transform not done yet
    if clen % 2: 
      w -= 1        # Meander has issues with oddness
      h -= 1
    mls        = []
    GH         = LineString([(w, y), (x, y)]) # West Bottom
    GE         = LineString([(w, y), (x, h)]) # North West
    GF         = LineString([(w, y), (w, h)]) # North Right
    EH         = LineString([(x, h), (x, y)]) # South Left
    EG         = LineString([(x, h), (w, y)]) # South East
    EF         = LineString([(x, h), (w, h)]) # East Top
    HF         = LineString([(x, y), (w, h)]) # North East
    FH         = LineString([(w, h), (x, y)]) # South West
    guideline  = {
      'NW': (GH, GE, GF),
      'SE': (EH, EG, EF),
      'SW': (EF, HF, GF),
      'NE': (GH, FH, EH)
    }
    return MultiLineString(guideline[facing])

  def collectPoints(self, guidelines):
    ''' collect the points intersecting the shape
        gridwalk the bounding box and collect Points() touching the guidelines
        grouped by the guidelines
    '''
    points  = []
    for i, gl in enumerate(list(guidelines.geoms)):
      points.append([]) # template
      start_x, stop_x, step_x, start_y, stop_y, step_y = self.orderGrid(gl)
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          if gl.intersects(pt):   # collect the points on the guideline
            points[i].append((x,y))
    if self.VERBOSE: self.pp.pprint(points)
    return points

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

  def makeDiagonals(self, points):
    ''' collapse a 2dim array of points into a single LineString
    '''
    sorted_points = []
    outer         = len(points)
    inner         = len(points[0])
    if self.VERBOSE: print(f'{outer=} {inner=}')
    for i in range(inner):
      if i % 2:  # odd
        start, stop, step = outer - 1, -1, -1
      else:      # even
        start, stop, step = 0, outer, 1
      for o in range(start, stop, step):
        if self.VERBOSE: 
          print(f'{o=} {i=} ', end='', flush=True) 
          print(f'{points[o][i]}', end='', flush=True) 
        sorted_points.append(points[o][i])
      if self.VERBOSE: print()
    return LineString(sorted_points)

'''
the
end
'''
