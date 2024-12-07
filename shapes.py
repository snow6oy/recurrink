import math
import pprint
import matplotlib.pyplot as plt
from shapely.geometry import box, LineString, Polygon, LinearRing 
from meander import Meander
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

  def __init__(self, direction=None, pencolor='000', name='R', **dim):
    self.name = name
    self.pencolor = pencolor
    if (len(dim)): # make a rectangle if we have dimensions
      #pp.pprint(dim)
      self.setDimensions(dim, direction, pencolor)
    else:
      pass # things that inherit from us .make() themselves

  def setDimensions(self, dim, direction, pencolor):
    x, y, w, h = dim.values()
    self.direction = direction if direction else 'N'
    ''' box defines the surface area for geom calculation
        access as r.box.bounds BUT be careful
        bounds are absolute unlike dimensions (width/height) which are relative
    '''
    self.box = box(x, y, x + w, y + h)
    #self.polygon = self.box  # alias for comparing against Parabolas that do not have boxen
    self.label = f'{self.name}{pencolor:<6}{int(x):>3}{int(y):>3}{int(x+w):>3}{int(y+h):>3}'
    ''' these FOUR are used by Flatten for collision detection
    '''
    self.w = LineString([(x, y), (x, y + h)])
    self.n = LineString([(x, y + h), (x + w, y + h)])
    self.s = LineString([(x, y), (x + w, y)])
    self.e = LineString([(x + w, y), (x + w, y + h)])

    # TODO boundary is also a Shapely property Name It Better or use box.boundary
    # boundary around the box for matplot
    self.boundary = LinearRing([(x, y), (x, y + h), (x + w, y + h), (x + w, y)])
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

  # TODO push meander conf outside self.__init__() and call from here
  # TODO test E and W
  def setSeeker(self, seeker, direction):
    ''' rewrite key geom values
    '''
    x, y, w, h = self.box.bounds
    X, Y, W, H = seeker.box.bounds
    self.direction = direction
    self.pencolor = seeker.pencolor
    #print("SET SEEKER self", x, y, w, h, " seeker ", X, Y, W, H, direction)
    if direction == 'N':
      self.box = box(X, h, W, H) 
      self.label = f'{self.name}{self.pencolor:<6}{int(X):>3}{int(h):>3}{int(W):>3}{int(H):>3}'
      self.boundary = LinearRing([(X, h), (X, H), (W, H), (W, h)])
    elif direction == 'E':
      self.box = box(w, Y, W, H) 
      self.label = f'{self.name}{self.pencolor:<6}{int(w):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
      self.boundary = LinearRing([(w, Y), (w, H), (W, H), (W, Y)])
    elif direction == 'S':
      self.box = box(X, Y, W, y) 
      self.label = f'{self.name}{self.pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(y):>3}'
      self.boundary = LinearRing([(X, Y), (X, y), (W, y), (W, Y)])
    elif direction == 'W':
      self.box = box(X, Y, x, H)
      self.label = f'{self.name}{self.pencolor:<6}{int(X):>3}{int(Y):>3}{int(x):>3}{int(H):>3}'
      self.boundary = LinearRing([(X, Y), (X, H), (x, H), (x, Y)])

  def dimensions(self):
    ''' return the orignal dimensions in order to make a new Rectangle()    
        the Pythonic way would be __deepcopy__ shenanigans
    '''
    dim = list(self.box.bounds)
    dim[2] -= dim[0]
    dim[3] -= dim[1]
    return tuple(dim)

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
      #plt.axis([0, 9, 0, 9])
    else:
      ax.plot(x, y)
      #plt.axis([0, 9, 0, 9])
    if fn:
      plt.savefig(f'tmp/{fn}.svg', format="svg")
    else:
      plt.show()

  def meander(self):
    ''' meander with padding and more
    print(list(self.box.exterior.coords))
    print(xywh)
    '''
    xywh =  list(self.box.exterior.coords)
    if self.direction in ['N', 'S']:
      #d = (90,405)
      d = ('EB','ET')
    elif self.direction in ['E', 'W']:
      #d = (0,360)
      d = ('NL','NR')
    m             = Meander(xywh)
    padme         = m.pad()
    guides        = m.guidelines(padme, d)
    points        = m.collectPoints(padme, guides)
    self.linefill = m.makeStripes(points)

  # TODO not used, either expose it as an option or remove
  def meanderWithoutPadding(self, gap=1):
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
    x, y, w, h = done.box.bounds
    X, Y, W, H = seeker.box.bounds
    pencolor = seeker.pencolor
    self.direction = direction

    if self.direction == 'NW':
      self.p2      = X
      self.start   = X
      self.stop    = w  # x + w
      self.oddline = H # y + h     # north odd
      self.outer   = y # y + sx      # south outer even
      self.inner   = h           # inner even
      # override Rectangle().boundary
      self.boundary = LinearRing([(X,Y), (X,H), (W,H), (W,h), (x,h), (x,Y)])
      self.label = f'{self.name}{pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
    elif self.direction == 'SE':
      self.p1      = x
      self.start   = Y # self.s
      self.stop    = h # self.n
      self.oddline = W # self.e # odd
      self.outer   = x # outer even
      self.inner   = w # inner even
      self.boundary = LinearRing([(x,Y), (x,y), (w,y), (w,h), (W,h), (W,Y)])
      self.label = f'{self.name}{pencolor:<6}{int(x):>3}{int(Y):>3}{int(W):>3}{int(h):>3}'
    else:
      raise NotImplementedError(f'direction {self.direction} lacking implementation')
    # get ready for Rectangle.meander()
    self.a = x
    self.b = w
    self.c = h
    self.d = y

  def meander(self):
    xywh = list(self.boundary.coords)
    if self.direction == 'NW':
      d = ('WB', 'NW', 'NR')
    elif self.direction == 'SE':
      d = ('SL', 'SE', 'ET')
    else:
      raise NotImplementedError(f'all at sea > {self.direction} <')
    m             = Meander(xywh)
    padme         = m.pad()
    guides        = m.guidelines(padme, d)
    points        = m.collectPoints(padme, guides)
    self.linefill = m.makeStripes(points)

class Parabola(Rectangle):
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  def __init__(self, seeker, done, direction):
    super().__init__(name = 'P')
    x, y, w, h     = done.box.bounds
    X, Y, W, H     = seeker.box.bounds
    self.pencolor  = seeker.pencolor
    self.direction = direction
    self.label     = f'{self.name}{self.pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
    self.clockwise = self.setClock(X, Y, W, H)

    if self.direction == 'N':
      self.p2      = Y
      self.start   = X
      self.stop    = W
      self.oddline = H
      self.outer   = Y
      self.inner   = h
      self.boundary = LinearRing([(X,Y), (X,H), (W,H), (W,Y), (w,Y), (w,h), (x,h), (x,Y)])
      self.gnomon   = [(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)]
      self.rectangl = [(w,y),(w,h),(W,h),(W,Y)]
    elif self.direction == 'W': 
      self.p1      = W
      self.start   = Y
      self.stop    = H
      self.oddline = X
      self.outer   = W
      self.inner   = x
      self.boundary = LinearRing([(X,Y), (X,H), (W,H), (W,h), (x,h), (x,y), (W,y), (W,Y)])
      ''' gnomon    = [(0,0),(0,18),(18,18),(18,12),(6,12),(6,0)]
          rectangle = [(6,0),(6,6),(18,6),(18,0)]
      '''
      self.gnomon   = [(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)]
      self.rectangl = [(x,Y),(x,y),(W,y),(W,Y)]
    elif self.direction == 'S':
      self.p2      = H
      self.start   = X
      self.stop    = W
      self.oddline = Y
      self.outer   = H
      self.inner   = y
      self.boundary = LinearRing([(X,Y), (X,H), (x,H), (x,y), (w,y), (w,H), (W,H), (W,Y)])
      self.gnomon   = [(X,Y),(X,H),(x,h),(x,y),(W,y),(W,Y)]
      self.rectangl = [(w,y),(w,h),(W,H),(W,y)]
    elif self.direction == 'E':
      self.p1      = X
      self.start   = Y
      self.stop    = H
      self.oddline = W
      self.outer   = X
      self.inner   = w
      self.boundary = LinearRing([(X,Y), (X,y), (w,y), (w,h), (X,h), (X,H), (W,H), (W,Y)])
      ''' these belong to Meander()
      '''
      self.gnomon   = [(X,h),(X,H),(W,H),(W,Y),(w,Y),(w,h)]
      self.rectangl = [(X,Y),(X,y),(w,y),(w,Y)]
      ''' end
      '''
    else:
      raise ValueError('no direction')
    # meander needs to know a,b,c,d
    # ALTHOUGH it could use self.boundary instead ???
    self.a = x
    self.b = w
    self.c = h
    self.d = y

  def meander(self):
    ''' Four Parabolas with padding and meander lines that go round corners
    '''
    g    = Meander(self.gnomon)
    gpad = g.pad()
    r    = Meander(self.rectangl)
    rpad = r.pad()

    if self.direction == 'N' and self.clockwise:  # t.parabola.Test.test_12
      gmls = g.guidelines(gpad, ('SR', 'SE', 'EB'))
      rmls = r.guidelines(rpad, ('NL', 'NR'))
    elif self.direction == 'N':                   # t.parabola.Test.test_5
      gmls = g.guidelines(gpad, ('EB', 'SE', 'SR'))
      rmls = r.guidelines(rpad, ('EB', 'ET'))
    elif self.direction == 'S' and self.clockwise: # t.parabola.Test.test_7
      gmls = g.guidelines(gpad, ('NR', 'NE', 'ET'))
      rmls = r.guidelines(rpad, ('EB', 'ET'))
    elif self.direction == 'S':                    # t.parabola.Test.test_6
      gmls = g.guidelines(gpad, ('ET', 'NE', 'NR'))
      rmls = r.guidelines(rpad, ('ET', 'EB'))
    elif self.direction == 'E' and self.clockwise: # t.parabola.Test.test_9
      gmls = g.guidelines(gpad, ('WB', 'SW', 'SL'))
      rmls = r.guidelines(rpad, ('SR', 'SL'))
    elif self.direction == 'E':                    # t.parabola.Test.test_8
      gmls = g.guidelines(gpad, ('SL', 'SW', 'WB'))
      rmls = r.guidelines(rpad, ('SL', 'SR'))
    elif self.direction == 'W':                    # t.parabola.Test.test_11
      if self.clockwise:
        gmls = g.guidelines(gpad, ('EB', 'SE', 'SR'))
      else:                                        # t.parabola.Test.test_10
        gmls = g.guidelines(gpad, ('SR', 'SE', 'EB')) 
      rmls = r.guidelines(rpad, ('WT', 'WB'))
    else:
      raise NotImplementedError(f'all at sea > {self.direction} <')
    """
    {self.direction=} {self.clockwise=} {self.gnomon=} {gmls=} 
    {self.rectangl=} {rmls=}
    """
    p1 = g.collectPoints(gpad, gmls)
    p2 = r.collectPoints(rpad, rmls)
    self.linefill = r.joinStripes(p1, p2)

  def setClock(self, X, Y, W, H):
    ''' meandering an odd number of stripes requires direction order to be clockwise
        even stripes must be anti-clockwise

        tests suggest that when num of stripes is 1 then clockwise should be True
        ignoring that corner case for now ..
    ''' 
    width     = W - X
    height    = H - Y
    clockwise = None     # difference between False and None is .. err
    if width == height:
      if width % 3:
        print(f"expected seeker to be divisible by 3 {width=}")
      else:
        raw_stripes   = (width - 1) / 3         # padding reduces width
        numof_stripes = math.floor(raw_stripes) # round down
        clockwise     = False if numof_stripes % 2 else True
        #print(f"{round(numof_stripes)=} {clockwise=}")
    else:
      pass
      # TODO fix tests with non-square seekers
      # raise ValueError(f"expected seeker to be square {width=} {height=}")
    return clockwise

class FakeBox:
  ''' wrap a Shapely Polygon with .box and .dimensions
      then it can pass as a Rectangle for the purpose of Cropping a Seeker
  '''
  def __init__(self, polygon):
    x, y, w, h =  list(polygon.exterior.bounds)
    self.w = LineString([(x, y), (x, h)])
    self.n = LineString([(x, h), (w, h)])
    self.s = LineString([(x, y), (w, y)])
    self.e = LineString([(w, y), (w, h)])
    self.box = box(x, y, w, h)  
    self.label = f"FAKEBOX {x} {y} {w} {h}"

  def dimensions(self):
    ''' copy of Rectangle.dimensions()
    '''
    dim = list(self.box.bounds)
    dim[2] -= dim[0]
    dim[3] -= dim[1]
    return tuple(dim)

'''
the
end
'''
