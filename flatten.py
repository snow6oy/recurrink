import sys
import matplotlib.pyplot as plt
import pprint
from shapely.geometry import box, LinearRing, Polygon, LineString
pp = pprint.PrettyPrinter(indent=2)

class Rectangle():
  ''' boxen

    n +---+---+---+   OUTER EDGES      POINTS
      |   |   |   |   n north          nw na nb ne
    c +---+---+---+   s south          wc ac bc ec
      |   |   |   |   e east           wd ad bd ed
    d +---+---+---+   w west           sw sa sb se
      |   |   |   |
    s +---+---+---+   INNER EDGES a b c d 
      w   a   b   e   used to calculate Gnomon and Parabola
  '''

  def __init__(self, direction=None, pencolor='000', name=None, **dim):
    self.name = name if name else 'R'
    if (len(dim)): # make a rectangle if we have dimensions
      self.set_dimensions(dim, direction, pencolor)
      #pp.pprint(dim)
    else:
      pass # things that inherit from us .make() themselves

  def set_dimensions(self, dim, direction, pencolor):
    x, y, w, h = dim.values()
    self.direction = direction if direction else 'N'
    self.label = f'{self.name}{pencolor:<6}{x:>3}{y:>3}{w:>3}{h:>3}'
    ''' box defines the surface area for geom calculation
        access as r.box.bounds BUT be careful
        bounds are absolute unlike dimensions (width/height) which are relative
    '''
    self.box = box(x, y, x + w, y + h)  
    ''' these FOUR are used by Flatten for collision detection
    '''
    self.w = LineString([(x, y), (x, y + h)])
    self.n = LineString([(x, y + h), (x + w, y + h)])
    self.s = LineString([(x, y), (x + w, y)])
    self.e = LineString([(x + w, y), (x + w, y + h)])

    self.boundary = LinearRing(     # boundary around the box for matplot
      [(x, y), (x, y + h), (x + w, y + h), (x + w, y), (x, y)]
    )
    ''' configure self.meander()
    '''
    if self.direction in ['E', 'W']:
      self.p1 = x
      self.start = y
      self.stop  = y + h
      self.d     = float("inf") # any value bigger than p2 is ok
      if (self.start % 2 == 0):  # odd and even must be absolute
        self.outer = x + w
        self.oddline = x
      else:
        self.outer = x
        self.oddline = x + w
    elif self.direction in ['N', 'S']:
      self.p2 = y
      self.start = x
      self.stop  = x + w
      self.a     = float("inf") # see self.d
      if (self.start % 2 == 0):  # odd and even must be absolute
        self.outer = y + h
        self.oddline = y
      else:
        self.outer = y
        self.oddline = y + h

  # TODO geom rename to transform AND push meander conf outside self.__init__() and call from here
  def set_seeker(self, seeker, direction):
    ''' rewrite key geom values
    '''
    x, y, w, h = self.box.bounds
    sx, sy, sw, sh = seeker.box.bounds
    # print(x, y, w, h, direction)
    self.direction = direction
    if direction == 'N':
      self.box = box(x, sh, w, h) 
      self.boundary = LinearRing([(x, sh), (x, h), (w, h), (w, sh), (x, sh)])
    elif direction == 'E':
      self.box = box(sw, y, w, h) 
      self.boundary = LinearRing([(sw, y), (sw, h), (w, h), (w, y), (sw, y)])
    elif direction == 'S':
      self.box = box(x, y, w, sy) 
      self.boundary = LinearRing([(x, y), (x, sy), (w, sy), (w, y), (x, y)])
    elif direction == 'W':
      self.box = box(x, y, sx, h) 
      self.boundary = LinearRing([(x, y), (x, h), (sx, h), (sx, y), (x, y)])

  def dimensions(self):
    ''' return the orignal dimensions in order to make a new Rectangle()    
        the Pythonic way would be __deepcopy__ shenanigans
    '''
    dim = list(self.box.bounds)
    dim[2] -= dim[0]
    dim[3] -= dim[1]
    return tuple(dim)

  '''
  def twins(self, seeker, direction):
    self.direction = direction
    if direction = 'W':
      self.boundary = LinearRing([(x, y), (x, h), (sx, h), (sx, y), (x, y)])
  '''

  def xyPoints(self):
    ''' Shapely has one list of x xpoints and another list of y points
        also useful for matplotlib
    '''
    return self.boundary.xy

  def printPoints(self):
    x, y = self.xyPoints()
    if len(x) == len(y):
      [print(f"{p:>2}", y[i]) for i, p in enumerate(x)]
    else:
      raise IndexError("uneven lists x and y")

  def plotPoints(self, seeker=None, fn=None, boundary=True):
    ''' matplot to svg on disk
        r1x = [0, 0, 1, 1, 2, 2, 0]
        r1y = [0, 2, 2, 1, 1, 0, 0]
        r2x = [2, 3, 3, 1, 1, 2, 2]
        r2y = [0, 0, 2, 2, 1, 1, 0] 
    '''
    if boundary:
      x, y = self.xyPoints() 
    else: # swap list format for plotter
     x = []
     y = []
     [x.append(c[0]) for c in self.linefill.coords]
     [y.append(c[1]) for c in self.linefill.coords]
    fig, ax = plt.subplots()   # Create a figure containing a single Axes.
    if seeker and boundary:
      x1, y1 = seeker.xyPoints()
      plt.plot(x, y, 'b-', x1, y1, 'r--')
      plt.axis([0, 9, 0, 9])
    else:
      ax.plot(x, y)
      #plt.axis([0, 9, 0, 9])
    if fn:
      # plt.figure(figsize=[6, 6])
      # plt.gca().set_position([0, 0, 1, 1])
      # plt.axis('off')
      # plt.axis([0, 9, 0, 9])
      plt.savefig(f'/tmp/{fn}.svg', format="svg")
    else:
      plt.show()

  def meander(self, gap=1):
    ''' meander chooses line depending on whether the coordinate is odd or even
        even lines vary depending on where the coordinate lies in the sequence
    '''
    points = []
    start = int(self.start)  # Shapely send floats
    stop  = int(self.stop + gap)
    if self.direction in ['N','S','NW']:
      p2 = self.p2
      # an uneven gap can cause the last line to stop short
      # stop + gap fixes that but there maybe a side-effect
      # that causes meander to leak across the Rectangle border
      for p1 in range(start, stop, gap):
        points.append([p1, p2])
        p3 = self.inner if p1 >= self.a and p1 <= self.b else self.outer
        p2 = p3 if (p1 % 2 == 0) else self.oddline
        points.append([p1, p2])
    elif self.direction in ['E','W','SE']:
      p1 = self.p1
      #print(f"meander d {self.direction} p1 {p1} d {self.d} c {self.c} in {self.inner} out {self.outer} ")
      for p2 in range(start, stop, gap):
        points.append([p1, p2])
        p3 = self.inner if p2 >= self.d and p2 <= self.c else self.outer
        p1 = p3 if (p2 % 2 == 0) else self.oddline
        points.append([p1, p2])
    #self.path = tuple(points)
    #self.linefill = LineString(points[:-1]) # boundaries are closed loops, unlike meander
    self.linefill = LineString(points) # boundaries are closed loops, unlike meander

class Gnomon(Rectangle):
  ''' Gnomon has an area of IDGP that equals HPFB
    D  G  C
    I  P  F
    A  H  B
    https://en.wikipedia.org/wiki/Theorem_of_the_gnomon

    two out of four possible gnomon can be drawn here
        NW  +---  SE     |
            |         ---+
  '''
  def __init__(self, seeker, done, direction=None):
    super().__init__(name = 'G')
    x, y, w, h = done
    X, Y, W, H = seeker
    self.direction = direction

    if self.direction == 'NW':
      self.p2 = x
      self.start = x
      self.stop  = w  # x + w
      self.oddline = h # y + h     # north odd
      self.outer = Y # y + sx      # south outer even
      self.inner = H           # inner even
      # override Rectangle().boundary
      self.boundary = LinearRing([(x,y), (x,h), (w,h), (w,H), (X,H), (X,y), (x,y)])
    elif self.direction == 'SE':
      self.p1 = X
      self.direction = 'SE'
      self.start = y # self.s
      self.stop  = H # self.n
      self.oddline = x + w # self.e # odd
      self.outer = X # outer even
      self.inner = W # inner even
      self.boundary = LinearRing([(X,y), (X,Y), (W,Y), (W,H), (w,H), (w,y), (X,y)])
    else:
      raise NotImplementedError(f'direction {self.direction} lacking implementation')
    # get ready for Rectangle.meander()
    self.a = X
    self.b = W
    self.c = H
    self.d = Y

class Parabola(Rectangle):
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  # TODO pass pencol to parent Rectangle()
  def __init__(self, seeker, done, direction):
    super().__init__(name = 'P')
    x, y, w, h = done
    X, Y, W, H = seeker
    self.direction = direction

    if self.direction == 'N':
      ''' these COULD belong to self.meander_conf{} ?
      '''
      self.p2      = y
      self.start   = x
      self.stop    = w
      self.oddline = h
      self.outer   = y
      self.inner   = H
      ''' end
      '''
      self.boundary = LinearRing([
        (x,y), (x,h), (w,h), (w,y), (W,y), (W,H), (X,H), (X,y), (x,y)
      ])
    elif self.direction == 'W': 
      self.p1    = w
      self.start = y
      self.stop  = h
      self.oddline = x
      self.outer = w
      self.inner = W
      self.boundary = LinearRing([
        (x,y), (x,h), (w,h), (w,H), (X,H), (X,Y), (w,Y), (w,y), (x,y)
      ])
    elif self.direction == 'S':
      self.p2 = h
      self.start = x
      self.stop  = w
      self.oddline = y
      self.outer = h
      self.inner = Y
      self.boundary = LinearRing([
        (x,y), (x,h), (X,h), (X,Y), (W,Y), (W,h), (w,h), (w,y), (x,y)
      ])
    elif self.direction == 'E':
      self.p1    = x
      self.start = y
      self.stop  = h
      self.oddline = w
      self.outer = x
      self.inner = X
      self.boundary = LinearRing([
        (x,y), (x,Y), (W,Y), (W,H), (x,H), (x,h), (w,h), (w,y), (x,y)
      ])
    else:
      raise ValueError('no direction')
    # meander needs to know a,b,c,d
    # ALTHOUGH it could use self.boundary instead ???
    self.a = X
    self.b = W
    self.c = H
    self.d = Y

class Flatten:
  def overlayTwoCells(self, s, done):
    ''' test the number of seeker edges that cross or are entirely inside done
        transform done into one or more shapes and return them as a list
    '''
    if s.w.intersects(done.w) and s.e.intersects(done.e) and s.n.disjoint(done.boundary): # test 7
      return self.split(s, done, required=[{'R':'S'}])
    elif s.w.intersects(done.w) and s.e.intersects(done.e): # test 7
      return self.split(s, done, required=[{'R':'N'}])
    elif s.n.intersects(done.n) and s.s.intersects(done.s) and s.e.disjoint(done.boundary): # test 7
      return self.split(s, done, required=[{'R':'W'}])
    elif s.n.intersects(done.n) and s.s.intersects(done.s): # test 7
      return self.split(s, done, required=[{'R':'E'}])
    elif s.n.crosses(done.e) and s.w.crosses(done.s):       # test 6
      return self.split(s, done, required=[{'G':'NW'}])
    elif s.n.crosses(done.w) and s.e.crosses(done.s): # test 6
      return self.split(s, done, required=[{'G':'NE'}])
    elif s.s.crosses(done.w) and s.e.crosses(done.n): # test 6
      return self.split(s, done, required=[{'G':'SE'}])
    elif s.w.crosses(done.n) and s.s.crosses(done.e): # test 6
      return self.split(s, done, required=[{'G':'SW'}])
    elif s.n.crosses(done.e) and s.s.crosses(done.w): # test 5
      return self.split(s, done, required=[{'R':'N'}, {'R':'S'}])
    elif s.e.crosses(done.n) and s.w.crosses(done.s): # test 5
      return self.split(s, done, required=[{'R':'E'}, {'R':'W'}])
    elif s.e.crosses(done.s) and s.w.crosses(done.s): # test 10
      return self.split(s, done, required=[{'P':'N'}])
    elif s.n.crosses(done.w) and s.s.crosses(done.w): # test 11
      return self.split(s, done, required=[{'P':'E'}])
    elif s.e.crosses(done.n) and s.w.crosses(done.n): # test 8 
      return self.split(s, done, required=[{'P':'S'}])
    elif s.n.crosses(done.e) and s.s.crosses(done.e): # test 9
      return self.split(s, done, required=[{'P':'W'}])
    elif s.box.within(done.box):                      # test 3 
      return self.split(s, done, required=[{'G':'NW'}, {'G':'SE'}])
    # print("Err Flatten.overlayTwoCells NO MATCH")
    return []

  def split(self, seeker, done, required=list()):
    shapes = []
    for r in required:
      for name in r:
        direction = r[name]
        if name == 'P':
          s = Parabola(seeker.box.bounds, done.box.bounds, direction=r[name]) # make shape geoms from two boxen
        elif name == 'G':
          s = Gnomon(seeker.box.bounds, done.box.bounds, direction=r[name]) # make shape geoms from two boxen
        elif name == 'R':
          x, y, w, h = done.dimensions()
          s = Rectangle(x=x, y=y, w=w, h=h)
          s.set_seeker(seeker, direction)
        else:
          raise ValueError(f"cannot split anonymous '{name}'")
        shapes.append(s)
    return shapes

if __name__ == '__main__':
  ''' make a parabola from two boxen
  '''
  f = Flatten()
  r1 = Rectangle(x=1, y=1, w=6, h=3)
  print(r1.name)
  r2 = Rectangle(x=3, y=2, w=2, h=3)
  shapes = f.overlayTwoCells(r2, r1)
  if len(shapes):
    shapes[0].plotPoints(seeker=r2) 
