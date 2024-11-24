import matplotlib.pyplot as plt
import pprint
from shapely import line_merge # set_precision
from shapely.geometry import Polygon, LineString, MultiLineString, Point
pp = pprint.PrettyPrinter(indent=2)

class Meander():
  def __init__(self, xywh, direction):
    self.shape   = Polygon(xywh) # a Shapely polygon
    ok = all(d in [0, 45, 90, 135, 180, 225, 270, 315, 360, 405, 450, 495] for d in direction)
    if not ok:
      raise ValueError(f"lost at sea {direction}")
    self.direction = direction

  def pad(self):
    ''' make a gap between cells by adding padding with Shapely.buffer
        a small Polygon may end up empty. Then silently return the original
    '''
    b = self.shape.buffer(-1, single_sided=True)
    #return set_precision(b, 2.0) print(b.is_empty)
    return self.shape if b.is_empty else self.shape

  # TODO direction is the list and test each available axis e.g. 0 in [45,225]
  def guidelines(self, padme):
    ''' define lines to guide meander
        both from direction by axis and by position
        degrees in the range 0-359 refer to an axis including diagonals e.g. 45 135 225 315
        the range >360 indicates the same axis but on the opposite side
        return guidelines with desired endpoints

  315   0    45		360                 E W         n   0 N 360
      ↖ ↑ ↗              ↑                 +---+        e  90 E 405
  270 ←   →  90    495 ←   → 405         n |   | N      s 180 S 450
      ↙ ↓ ↘              ↓               s +---+ S      w 270 W 495
  225  180  135		450                 e w
    '''
    x, y, w, h = padme.bounds
    mls        = []
    glines     = {
        0 : LineString([(x, y), (x, h)]),
       45 : LineString([(x, y), (w, h)]),
       90 : LineString([(x, y), (w, y)]),
      135 : LineString([(x, h), (w, y)]),
      180 : LineString([(x, h), (x, y)]), 
      225 : LineString([(w, h), (x, y)]),
      270 : LineString([(w, y), (x, y)]),
      315 : LineString([(w, y), (x, h)]),
      360 : LineString([(w, y), (w, h)]),
      405 : LineString([(x, h), (w, h)]),
      450 : LineString([(w, h), (w, y)]),  
      495 : LineString([(w, h), (x, h)])   # that too
    }
    [mls.append(glines[d]) for d in self.direction]
    return MultiLineString(mls)

  # TODO 495 450 no-one else ?
  def orderGrid(self, padme, guidelines):
    ''' private method to simplify collectPoints()
    '''
    grid_order = []
    bx, by, bX, bY = list(padme.bounds)
    #print(bx, by, bX, bY)
    for i, gl in enumerate(list(guidelines.geoms)):
      if self.direction[i] >= 180 and self.direction[i] < 360 or self.direction[i] == 495:
        start_x, stop_x, step_x = int(bX), int(bx - 1), -1
      else:
        start_x, stop_x, step_x = int(bx), int(bX + 1), 1
      if self.direction[i] > 90 and self.direction[i] <= 270 or self.direction[i] == 450:
        start_y, stop_y, step_y = int(bY), int(by - 1), -1
      else:
        start_y, stop_y, step_y = int(by), int(bY + 1), 1
      grid_order.append([start_x, stop_x, step_x, start_y, stop_y, step_y])
    return grid_order

  def collectPoints(self):
    ''' collect the points intersecting the padded version of shape
        gridwalk the bounding box and collect Points() touching the guidelines
        grouped by the guidelines
    '''
    padme      = self.pad()
    guidelines = self.guidelines(padme)
    grid_order = self.orderGrid(padme, guidelines)
    points     = []
    same       = 0
    for i, gl in enumerate(list(guidelines.geoms)):
      points.append([]) # template
      start_x, stop_x, step_x, start_y, stop_y, step_y = grid_order[i]
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          t  = ' '
          if padme.covers(pt):      # surface test for gnomons
            if gl.intersects(pt):   # collect the points on the guideline
              points[i].append((x,y))
              t = '*'
          #print(f" {x},{y}{t}", end='', flush=True)
        #print('.')
      if i > 0 and len(points[i]) is not same:
        raise TypeError(f"{self.direction[i]} has {len(points[i])} points which is not {same}")
      same = len(points[i])
    return points

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
    writer = Plotter()
    #last_p1 = p1[-1][-1] # last point in Gnomon boundary
    writer.plotLine(s2, 'test_8')
    #print(f"{last_p1=} {s2[0]=}")
    #print(f"{list(s2.coords)=}")
    '''
    s1  = self.makeStripes(p1)
    last_p1 = list(s1.coords)[-1] # sort the points before marking the last
    s2  = self.makeStripes(p2)
    s2  = list(s2.coords)      # extract list from LineString
    s2  = list(reversed(s2))
    s2.insert(0, last_p1) # guess that last p1 matches first p2
    s2  = LineString(s2)
    mls = MultiLineString([s1, s2])

    stripe  = line_merge(mls)
    if stripe.geom_type != 'LineString':
      raise TypeError(f"line merge failed {stripe.geom_type}")
    return stripe

class Plotter():
  ''' wrapper around matplot so we can see whats going on
  '''
  def plot(self, p1, p2, fn):
    x1, y1 = p1.boundary.xy
    x2, y2 = p2.boundary.xy
    plt.plot(x1, y1, 'b-', x2, y2, 'r--')
    plt.axis([0, 18, 0, 18])
    plt.savefig(f'tmp/{fn}.svg', format="svg")

  def plotLine(self, line, fn):
    fig, ax = plt.subplots()
    x = []
    y = []
    [x.append(c[0]) for c in line.coords]
    [y.append(c[1]) for c in line.coords]
    ax.plot(x, y)
    plt.savefig(f'tmp/{fn}.svg', format="svg")
'''
the
end
'''
