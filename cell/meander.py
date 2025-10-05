import pprint
from shapely.geometry import Point, LineString, MultiLineString

class Line:

  # VERBOSE see children
  pp      = pprint.PrettyPrinter(indent=2)

  def guidelines(self, facing, clen, bounds):
    '''  E - B - F
         |       |
         A       C
         |       |
         H - D - G 
    '''
    x, y, w, h = bounds  # X,Y because Shapely Transform not done yet
    if clen % 2:    # Consider this to be padding ?
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
    HE         = LineString([(x, y), (x, h)]) # North Left
    HG         = LineString([(x, y), (w, y)]) # East Bottom
    FH         = LineString([(w, h), (x, y)]) # South West
    FG         = LineString([(w, h), (w, y)]) # South Right
    FE         = LineString([(w, h), (x, h)]) # South Right
    guideline  = {
       'N': (EH, FG),
       'S': (HE, GF),
       'E': (EF, HG),
       'W': (FE, GH),
      'NW': (GH, GE, GF),
      'SE': (EH, EG, EF),
      'SW': (EF, HF, GF),
      'NE': (GH, FH, EH),
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

  def makeStripes(self, points):
    ''' collapse a 2dim array of points into a single LineString
    '''
    #self.pp.pprint(points)
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
          #print(f'{o=} {i=} ', end='', flush=True) 
          print(f'|{points[o][i]}| ', end='', flush=True) 
        sorted_points.append(points[o][i])
      if self.VERBOSE: print()
    return LineString(sorted_points)

  def sliceByThird(self, facing, points):
    ''' make diagonals covers the entire square
        to convert to a gnomon the meandered line is shortened by 3
    '''
    ptlen     = len(points)
    if ptlen % 3: raise ValueError(f'Ouch! {ptlen} is not divisible by three')
    if facing == 'NW' or facing == 'SE':
      start   = int((ptlen / 3) * 2) - 1
      stop    = -1
    elif facing == 'SW' or facing == 'NE':
      start   = 0
      stop    = int(ptlen / 3) - 1
    #print(f'{start=} {stop=}')
    return points[start:stop]

'''
the
end
'''
