import sys
import matplotlib.pyplot as plt
class Rectangle:
  ''' helper class to elaborate rectangle

    n +---+---+---+   OUTER EDGES      POINTS
      |   |   |   |   n north          nw na nb ne
    c +---+---+---+   s south          wc ac bc ec
      |   |   |   |   e east           wd ad bd ed
    d +---+---+---+   w west           sw sa sb se
      |   |   |   |
    s +---+---+---+   INNER EDGES a b c d 
      w   a   b   e   used to calculate Gnomon and Parabola
  '''
  class Point:
    def __init__(self, x, y):
      self.x = x
      self.y = y
      self.p = tuple([x, y])
  def __init__(self, coordinates, dimensions, direction=None):
    x, y = coordinates
    w, h = dimensions
    # corners have points
    self.sw = self.Point(x, y)
    self.nw = self.Point(x, y + h)
    self.ne = self.Point(x + w, y + h)
    self.se = self.Point(x + w, y)
    # edges have lines
    self.w = x
    self.n = y + h
    self.s = y
    self.e = x + w
    self.dimensions = dimensions 
    if direction == 'E' or direction == 'W':
      self.p1 = self.w
      self.direction = 'E'
      self.start = self.s
      self.stop  = self.n
      self.d     = float("inf") # any value bigger than p2 is ok
      if (self.start % 2 == 0):  # odd and even must be absolute
        self.outer = self.e
        self.oddline = self.w
      else:
        self.outer = self.w
        self.oddline = self.e
    elif direction == 'N' or direction == None:
      self.p2 = self.s
      self.direction = 'N'
      self.start = self.w
      self.stop  = self.e
      self.a     = float("inf") # see self.d
      if (self.start % 2 == 0):  # odd and even must be absolute
        self.outer = self.n
        self.oddline = self.s
      else:
        self.outer = self.s
        self.oddline = self.n
    else:  # fallback for S and W but meander will break
      self.direction = direction 
    self.path = tuple([self.sw.p, self.nw.p, self.ne.p, self.se.p, self.sw.p])
  def compare(self, lo):
    ''' Booleans that may become true after comparing
    with another rectangle and finding a point or EDG within our boundary
    '''
    self.EAST      = True if self.sw.x > lo.sw.x and self.se.x < lo.se.x else False
    self.NORTH     = True if self.sw.y > lo.sw.y and self.ne.y < lo.ne.y else False
    self.SOUTHWEST = True if self.sw.x > lo.sw.x and self.sw.x < lo.se.x and self.sw.y > lo.sw.y and self.sw.y < lo.ne.y else False 
    self.NORTHWEST = True if self.nw.x > lo.sw.x and self.nw.x < lo.se.x and self.nw.y > lo.sw.y and self.nw.y < lo.ne.y else False 
    self.NORTHEAST = True if self.ne.x > lo.sw.x and self.ne.x < lo.se.x and self.ne.y > lo.sw.y and self.ne.y < lo.ne.y else False 
    self.SOUTHEAST = True if self.se.x > lo.sw.x and self.se.x < lo.se.x and self.se.y > lo.sw.y and self.se.y < lo.ne.y else False 
    self.NEDG      = True if self.n < lo.n and self.n > lo.s and self.e >= lo.e and self.w <= lo.w else False
    self.EEDG      = True if self.e < lo.e and self.e > lo.w and self.n >= lo.n and self.s <= lo.s else False
    self.SEDG      = True if self.s > lo.s and self.s < lo.n and self.e >= lo.e and self.w <= lo.w else False
    self.WEDG      = True if self.w > lo.w and self.w < lo.e and self.n >= lo.n and self.s <= lo.s else False
  def meander(self, gap=1):
    ''' meander chooses a line depending on whether the coordinate is odd or even
        even lines vary depending on where the coordinate lies in the sequence
    '''
    points = []
    if self.direction in ['N','S','NW']:
      p2 = self.p2
      # an uneven gap can cause the last line to stop short
      # stop + gap fixes that but there maybe a side-effect
      # that causes meander to leak across the Rectangle border
      for p1 in range(self.start, self.stop + gap, gap):
        points.append([p1, p2])
        p3 = self.inner if p1 >= self.a and p1 <= self.b else self.outer
        p2 = p3 if (p1 % 2 == 0) else self.oddline
        points.append([p1, p2])
    elif self.direction in ['E','W','SE']:
      p1 = self.p1
      for p2 in range(self.start, self.stop + gap, gap):
        points.append([p1, p2])
        p3 = self.inner if p2 >= self.d and p2 <= self.c else self.outer
        p1 = p3 if (p2 % 2 == 0) else self.oddline
        points.append([p1, p2])
    self.path = tuple(points)
  def xyPoints(self):
    ''' convert rectangle into one list of x xpoints and another list of y points
        useful for matplotlib
    '''
    x = [point[0] for point in self.path]
    y = [point[1] for point in self.path]
    return x, y
  def printPoints(self):
    x, y = self.xyPoints()
    if len(x) == len(y):
      [print(f"{p:>2}", y[i]) for i, p in enumerate(x)]
    else:
      raise IndexError("uneven lists x and y")
  def plotPoints(self, lower=None):
    ''' r1x = [0, 0, 1, 1, 2, 2, 0]
        r1y = [0, 2, 2, 1, 1, 0, 0]
        r2x = [2, 3, 3, 1, 1, 2, 2]
        r2y = [0, 0, 2, 2, 1, 1, 0] 
    '''
    x, y = self.xyPoints()
    fig, ax = plt.subplots()   # Create a figure containing a single Axes.
    if lower:
      x1, y1 = lower.xyPoints()
      plt.plot(x, y, 'r-', x1, y1, 'b--')
      plt.axis([0, 9, 0, 9])
    else:
      ax.plot(x, y)
      #plt.axis([0, 9, 0, 9])
    plt.show()   
class Gnomon(Rectangle):
  ''' Gnomon has an area of IDGP that equals HPFB
    D  G  C
    I  P  F
    A  H  B
    https://en.wikipedia.org/wiki/Theorem_of_the_gnomon
  '''
  def __init__(self, coordinates, dimensions, direction=None, edges=dict()):
    ''' two out of four possible gnomon can be drawn
        NW  +---  SE     |
            |         ---+
    '''
    super().__init__(coordinates, dimensions)
    # to be compatible with Parabola
    self.p1 = self.p2 = self.w
    self.a = edges['a']
    self.b = edges['b']
    self.c = edges['c']
    self.d = edges['d']
    self.nb = self.Point(self.n, self.b)
    self.sa = self.Point(self.a, self.s)
    self.ec = self.Point(self.e, self.c)
    self.wa = self.Point(self.w, self.a)
    self.wd = self.Point(self.w, self.d)
    self.ac = self.Point(self.a, self.c)
    self.bd = self.Point(self.b, self.d)
    if direction == 'SE':
      self.direction = 'SE'
      self.start = self.s
      self.stop  = self.n
      self.oddline = self.e # odd
      self.outer = self.a # outer even
      self.inner = self.b # inner even
      self.path = tuple([self.sw.p, self.wd.p, self.bd.p, self.nb.p, self.ne.p, self.se.p, self.sw.p])
    else:
      self.direction = 'NW'
      self.start = self.w
      self.stop  = self.e
      self.oddline = self.n # odd
      self.outer = self.s # outer even
      self.inner = self.c # inner even
      self.path = tuple([self.sw.p, self.nw.p, self.ne.p, self.ec.p, self.ac.p, self.sa.p, self.sw.p])
class Parabola(Rectangle):
  ''' u-shaped parallelogram
  '''
  def __init__(self, coordinates, dimensions, direction=None, edges=dict()):
    super().__init__(coordinates, dimensions)
    self.direction = direction
    # define inner lines
    self.a = edges['a']
    self.b = edges['b']
    self.c = edges['c']
    self.d = edges['d']
    # inner corners too
    self.ac = self.Point(self.a, self.c)
    self.ad = self.Point(self.a, self.d)
    self.bc = self.Point(self.b, self.c)
    self.bd = self.Point(self.b, self.d)
    # also intersection of inner and outer edges
    self.na = self.Point(self.a, self.n)
    self.nb = self.Point(self.b, self.n)
    self.sa = self.Point(self.a, self.s)
    self.sb = self.Point(self.b, self.s)
    self.ec = self.Point(self.e, self.c)
    self.ed = self.Point(self.e, self.d)
    self.wc = self.Point(self.w, self.c)
    self.wd = self.Point(self.w, self.d)
    # lookups based on direction
    self.path = []
    if direction == 'N':
      self.p2    = self.s
      self.start = self.w
      self.stop  = self.e
      self.oddline = self.n
      self.outer = self.s
      self.inner = edges['d']
      self.path = tuple([self.sw.p, self.nw.p, self.ne.p, self.se.p, self.sb.p, self.bd.p, self.ad.p, self.sa.p, self.sw.p])
    elif direction == 'S':
      self.p2 = self.n
      self.start = self.w
      self.stop  = self.e
      self.oddline = self.s
      self.outer = self.n
      self.inner = edges['c']
      self.path = tuple([self.sw.p, self.nw.p, self.na.p, self.ac.p, self.bc.p, self.nb.p, self.ne.p, self.se.p, self.sw.p])
    elif direction == 'E':
      self.p1    = self.w
      self.start = self.s
      self.stop  = self.n
      self.oddline = self.e
      self.outer = self.w
      self.inner = edges['a']
      self.path = tuple([self.sw.p, self.wd.p, self.ad.p, self.ac.p, self.wc.p, self.nw.p, self.ne.p, self.se.p, self.sw.p])
    elif direction == 'W':
      self.p1    = self.e
      self.start = self.s
      self.stop  = self.n
      self.oddline = self.w
      self.outer = self.e
      self.inner = edges['b']
      self.path = tuple([self.sw.p, self.nw.p, self.ne.p, self.ec.p, self.bc.p, self.bd.p, self.ed.p, self.se.p, self.sw.p])
class Flatten:
  '''
1. call gdoc writer from Outfile.gdoc 
2. writer will collapse three layers into one
   starting from the lower layer to the highest (bg > gf > top) 
   test each lower cell against all other upper cells 
   if the colour is the same then continue ..
3. at the point that cells intersect split or transform the lower cell
   try to facilitate continuous drawing to avoid unecessary pen up/down
   count how many edges are to be added to the lower cell (0-4)
   so that the lower cell is adjacent to the upper cell
4. now each cell is on a single plane
meander across each shape to create a zigzag fill
inject pen up/down commands at the shape boundary
  '''
  def overlayTwoCells(self, lo, up):
    ''' define how many parallelograms are required to transform lower
    and the direction that meander should take when hatching
    '''
    up.compare(lo)
    direction = ''
    if up.NORTHWEST and up.SOUTHEAST:  # test 6
      count = 4
    # test 7 
    elif up.NORTHWEST and up.SOUTHWEST:
      count = 3
      direction = 'W'
    elif up.NORTHEAST and up.SOUTHEAST:
      count = 3
      direction = 'E'
    elif up.SOUTHWEST and up.SOUTHEAST:
      count = 3
      direction = 'S'
    elif up.NORTHWEST and up.NORTHEAST: 
      count = 3
      direction = 'N'
    elif up.NORTHEAST or up.SOUTHWEST or up.SOUTHEAST or up.NORTHWEST: # test 9
      count = 2
    elif up.NEDG and up.SEDG: # tests 10-12
      count = 2
      direction = 'E'
    elif up.NEDG or up.SEDG:
      count = 1
      direction = 'E'
    elif up.EEDG and up.WEDG:
      count = 2
      direction = 'N'
    elif up.EEDG or up.WEDG:
      count = 1
      direction = 'N'
    else: # tests 13-14
      count = 0
    return count, direction
  def splitLowerUpper(self, count, lo, up, direction=None):
    ''' clockwise around the lower adding rectangles according to count
    generate the new rectangles and replace the old lower rectangle 
    2-----3
    | 5-9-4/8
    | | | |
    | 1-0 |
    1-6---7 '''
    shapes = list()
    if count == 4:
      e = {'a':up.w, 'b':(lo.e + 1), 'c':up.nw.y, 'd':None}
      # print(e)
      nw = Gnomon(coordinates=(lo.sw.x, lo.sw.y), edges=e, dimensions=lo.dimensions, direction='NW')
      shapes.append(nw)
      x2 = up.sw.x
      y2 = lo.sw.y
      w2 = up.se.x - lo.sw.x
      h2 = up.nw.y - lo.sw.y
      # for example 'a': 10, 'b': 20, 'c': 20, 'd': 10 with dimensions  20,20 
      b = up.se.x
      d = up.sw.y
      #a = lo.se.x + up.sw.x - b
      a = up.w
      #c = lo.se.y + up.sw.y - d
      c = up.n
      e={'a':a, 'b':up.se.x, 'c':up.se.y, 'd':up.sw.y}
      se = Gnomon(coordinates=(x2, y2), edges={'a':a, 'b':b, 'c':c, 'd':d}, dimensions=(w2, h2), direction='SE')
      shapes.append(se)
    elif count == 3:
      if direction == 'N':
        e = { 'a':up.w, 'b':up.e, 'c':None, 'd':up.n }
      elif direction == 'S':
        e = { 'a':up.w, 'b':up.e, 'c':up.s, 'd':None }
      elif direction == 'E':
        e = { 'a':up.e, 'b':None, 'c':up.n, 'd':up.s }
      elif direction == 'W':
        e = { 'a':None, 'b':up.w, 'c':up.n, 'd':up.s }
      else:
        raise ValueError(f"Parabola does not know '{direction}' direction")
      p = Parabola(coordinates=(lo.sw.x, lo.se.y), edges=e, dimensions=lo.dimensions, direction=direction)
      shapes.append(p)
    elif count == 2:
      if direction == 'N':
        w1 = lo.e - up.e
        w2 = up.w - lo.w
        h = lo.n - lo.s
        e = Rectangle(coordinates=(up.se.x, up.se.y), dimensions=(w1, h), direction='E')
        shapes.append(e)
        w = Rectangle(coordinates=(lo.sw.x, lo.sw.y), dimensions=(w2, h), direction='W')
        shapes.append(w)
    else:
      raise ValueError(f'{count} {direction} not done')
    return shapes
  def draw(self, r1x, r1y, r2x, r2y):
    ''' r1x = [0, 0, 1, 1, 2, 2, 0]
        r1y = [0, 2, 2, 1, 1, 0, 0]
        r2x = [2, 3, 3, 1, 1, 2, 2]
        r2y = [0, 0, 2, 2, 1, 1, 0] 
    '''
    #print(r1x, r1y)
    plt.plot(r1x, r1y, 'r-', r2x, r2y, 'b--')
    plt.axis([0, 9, 0, 9])
    #plt.label(r1name + r2name)
    plt.show()
if __name__ == '__main__':
  ''' look here for visual testing with matplot otherwise see unittest
  '''
  lo = Rectangle(coordinates=(1, 1), dimensions=(4, 4))
  up = Rectangle(coordinates=(2, 2), dimensions=(2, 2))
  f = Flatten()
  t = int(sys.argv[1])
  # TODO refactor from Parabola
  #############
  # Rectangles
  #############
  if t == 1:
    print(up.xyPoints()) 
    up.plotPoints(lower=lo)
  elif t == 2:  # meander N or E
    #r = Rectangle(coordinates=(1, 1), dimensions=(6, 6))
    #r.meander(direction='E', gap=1)
    r = Rectangle(coordinates=(1, 1), dimensions=(6, 6), direction='N')
    r.meander()
    r.printPoints()
    r.plotPoints()
  #---------+
  # Gnomons |
  #---------+
  elif t == 3: # plot gnomons
    f.draw(
      [2,1,1,5,5,2,2,5,5,4,4,2,2], 
      [1,1,5,5,4,4,1,1,4,4,2,2,1],
      [2,2,4,4,2], 
      [2,4,4,2,2]
    )
  elif t == 4:  # calculate gnomons 
    count, d = f.overlayTwoCells(lo, up)
    shapes = f.splitLowerUpper(count, lo, up)
    shapes[1].printPoints()
    shapes[0].plotPoints(lower=shapes[1])
  elif t == 5: # create gnomon paths 
    g = Gnomon(coordinates=(1,1), edges={'a':2,'b':None,'d':None,'c':4}, dimensions=(4,4))
    g.printPoints()
    g.plotPoints()
  elif t == 6: # gnomon south east
    g = Gnomon(coordinates=(2,1), edges={'a':2,'b':4,'c':4,'d':2}, dimensions=(3,3), direction='SE')
    g.printPoints()
    g.plotPoints()
  elif t == 7: # meander gnomons
    g1 = Gnomon(coordinates=(1,1), edges={'a':2,'b':5,'d':None,'c':4}, dimensions=(4,4))
    g1.printPoints()
    g1.meander()
    print('-'*80)
    '''
    g1.plotPoints()
    g2.plotPoints()
    '''
    g2 = Gnomon(coordinates=(2,1), edges={'a':2,'b':4,'c':4,'d':2}, dimensions=(3,3), direction='SE')
    g2.meander()
    g2.printPoints()
    g1.plotPoints(lower=g2)
  elif t == 8:
    g = Gnomon(coordinates=(0,0), edges={'a': 9, 'b': 31, 'c': 20, 'd': None}, dimensions=(30,30), direction='NW')
    g.meander()
    g.plotPoints()
  elif t == 9:
    g = Gnomon(coordinates=(10,0), edges={'a': 10, 'b': 20, 'c': 20, 'd': 10}, dimensions=(20,20), direction='SE')
    g.meander()
    g.plotPoints()

  #===========#
  # Parabolas #
  #-----------#
  elif t == 10: # north facing parabola
    lo = Rectangle(coordinates=(1, 1), dimensions=(6, 2))
    up = Rectangle(coordinates=(3, 0), dimensions=(2, 2))
    numof_edges, d = gcw.overlayTwoCells(lo, up)
    shapes = gcw.splitLowerUpper(numof_edges, lo, up, direction=d)
    #shapes[0].printPoints()
    up.plotPoints(lower=shapes[0])
  elif t == 11: # south facing parabola
    lo = Rectangle(coordinates=(1, 1), dimensions=(6, 3))
    up = Rectangle(coordinates=(3, 2), dimensions=(2, 3))
    numof_edges, d = gcw.overlayTwoCells(lo, up)
    shapes = gcw.splitLowerUpper(numof_edges, lo, up, direction=d)
    #shapes[0].printPoints()
    up.plotPoints(lower=shapes[0])
  elif t == 12:  # calculate parabola and draw path
    lo = Rectangle(coordinates=(1, 1), dimensions=(6, 6))
    up = Rectangle(coordinates=(3, 1), dimensions=(2, 2))
    count, d = gcw.overlayTwoCells(lo, up) 
    shapes = gcw.splitLowerUpper(count, lo, up, direction=d)
    shapes[0].plotPoints()
  elif t == 13: # parabola meander
    #p = Parabola(coordinates=(1,1), edges={'a':3,'b':5,'c':None,'d':3}, dimensions=(6,6), direction='N') # north
    p = Parabola(coordinates=(1,1), edges={'a':3,'b':5,'c':5,'d':None}, dimensions=(6,6), direction='S') # south
    #p = Parabola(coordinates=(1,1), edges={'a':3,'b':None,'c':5,'d':3}, dimensions=(6,6), direction='E') # east
    #p = Parabola(coordinates=(1,1), edges={'a':None,'b':5,'c':5,'d':3}, dimensions=(6,6), direction='W') # west
    p.meander()
    p.printPoints()
    p.plotPoints()
  else:
    print('bye')
