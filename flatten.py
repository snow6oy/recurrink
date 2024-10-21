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

  def __init__(self, direction=None, pencolor='000', name='R', **dim):
    self.name = name
    self.pencolor = pencolor
    if (len(dim)): # make a rectangle if we have dimensions
      #pp.pprint(dim)
      self.set_dimensions(dim, direction, pencolor)
    else:
      pass # things that inherit from us .make() themselves

  def set_dimensions(self, dim, direction, pencolor):
    x, y, w, h = dim.values()
    self.direction = direction if direction else 'N'
    ''' box defines the surface area for geom calculation
        access as r.box.bounds BUT be careful
        bounds are absolute unlike dimensions (width/height) which are relative
    '''
    self.box = box(x, y, x + w, y + h)  
    self.label = f'{self.name}{pencolor:<6}{int(x):>3}{int(y):>3}{int(x+w):>3}{int(y+h):>3}'
    ''' these FOUR are used by Flatten for collision detection
    '''
    self.w = LineString([(x, y), (x, y + h)])
    self.n = LineString([(x, y + h), (x + w, y + h)])
    self.s = LineString([(x, y), (x + w, y)])
    self.e = LineString([(x + w, y), (x + w, y + h)])

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
  def set_seeker(self, seeker, direction):
    ''' rewrite key geom values
    '''
    x, y, w, h = self.box.bounds
    X, Y, W, H = seeker.box.bounds
    self.direction = direction
    self.pencolor = seeker.pencolor
    #print("SET SEEKER self", x, y, w, h, " seeker ", X, W, Y, H, direction)
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
    x, y, w, h = done.box.bounds
    X, Y, W, H = seeker.box.bounds
    pencolor = seeker.pencolor
    self.direction = direction

    if self.direction == 'NW':
      self.p2      = X
      self.start   = X
      self.stop    = W  # x + w
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

class Parabola(Rectangle):
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  # TODO pass pencol to parent Rectangle()
  def __init__(self, seeker, done, direction):
    super().__init__(name = 'P')
    x, y, w, h = done.box.bounds
    X, Y, W, H = seeker.box.bounds
    pencolor = seeker.pencolor
    self.direction = direction

    if self.direction == 'N':
      ''' these COULD belong to Meander()
      '''
      self.p2      = Y
      self.start   = X
      self.stop    = W
      self.oddline = H
      self.outer   = Y
      self.inner   = h
      ''' end
      '''
      self.boundary = LinearRing([(x,y), (x,h), (w,h), (w,y), (W,y), (W,H), (X,H), (X,y)])
    elif self.direction == 'W': 
      self.p1      = W
      self.start   = Y
      self.stop    = H
      self.oddline = X
      self.outer   = W
      self.inner   = w
      self.boundary = LinearRing([(X,Y), (X,H), (W,H), (W,h), (x,h), (x,y), (W,y), (W,Y)])
      self.label = f'{self.name}{pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
    elif self.direction == 'S':
      self.p2      = H
      self.start   = X
      self.stop    = W
      self.oddline = Y
      self.outer   = H
      self.inner   = y
      self.boundary = LinearRing([(X,Y), (X,H), (x,H), (x,y), (w,y), (w,H), (W,H), (W,Y)])
      self.label = f'{self.name}{pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
    elif self.direction == 'E':
      self.p1      = X
      self.start   = Y
      self.stop    = H
      self.oddline = W
      self.outer   = X
      self.inner   = x
      self.boundary = LinearRing([(X,Y), (X,y), (w,y), (w,h), (X,h), (X,H), (W,H), (W,Y)])
      self.label = f'{self.name}{pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'
    else:
      raise ValueError('no direction')
    # meander needs to know a,b,c,d
    # ALTHOUGH it could use self.boundary instead ???
    self.a = x
    self.b = w
    self.c = h
    self.d = y

class Flatten:

  def sameBoxen(self, seeker, done):
    return seeker.box.equals(done.box)

  def split(self, seeker, done, required=list()):
    shapes = []
    #print(required)
    for r in required:
      for name in r:
        direction = r[name]
        if name == 'P': # make shape geoms from two boxen
          s = Parabola(seeker, done, direction=r[name]) 
        elif name == 'G':
          s = Gnomon(seeker, done, direction=r[name]) 
        elif name == 'R':
          x, y, w, h = done.dimensions()
          s = Rectangle(x=x, y=y, w=w, h=h) # copy of done
          s.set_seeker(seeker, direction)   # transform done copy into seeker
        else:
          raise ValueError(f"cannot split anonymous '{name}'")
        shapes.append(s)
    return shapes

  def __overlayTwoCells(self, s, done):
    ''' test the number of seeker edges that cross or are entirely inside done
        ignore edges that touch but do not cross
        transform done into one or more shapes and return them as a list
    '''
    #print(s.box.bounds, done.box.bounds)
    if s.box.equals(done.box): # rectangle t16 
      return []
    # next four tests rectangle t14
    elif s.w.intersects(done.w) and s.e.intersects(done.e) and s.n.disjoint(done.boundary): 
      return [] if s.s.covers(done.n) else self.split(s, done, required=[{'R':'N'}])
    elif s.w.intersects(done.w) and s.e.intersects(done.e): 
      return [] if s.n.covers(done.s) else self.split(s, done, required=[{'R':'S'}])
    elif s.n.intersects(done.n) and s.s.intersects(done.s) and s.e.disjoint(done.boundary):
      return [] if s.w.covers(done.e) else self.split(s, done, required=[{'R':'E'}])
    elif s.n.intersects(done.n) and s.s.intersects(done.s):
      return [] if s.e.covers(done.w) else self.split(s, done, required=[{'R':'W'}])
    elif s.n.crosses(done.e) and s.w.crosses(done.s):       # test 6
      #return self.split(s, done, required=[{'G':'NW'}])
      # TODO return a Gnomon
      return self.split(s, done, required=[{'R':'S'}, {'R':'E'}])
    elif s.n.crosses(done.w) and s.e.crosses(done.s): # test 6
      return self.split(s, done, required=[{'G':'NE'}])
    elif s.s.crosses(done.w) and s.e.crosses(done.n): # test 6
      return self.split(s, done, required=[{'R':'E'}, {'R':'W'}])
      #return self.split(s, done, required=[{'G':'SE'}])
    elif s.w.crosses(done.n) and s.s.crosses(done.e): # test 6
      return self.split(s, done, required=[{'G':'SW'}])
    elif s.n.crosses(done.e) and s.s.crosses(done.w): # test 5
      return self.split(s, done, required=[{'R':'E'}, {'R':'W'}])
    elif s.e.crosses(done.n) and s.w.crosses(done.s): # test 5
      return self.split(s, done, required=[{'R':'N'}, {'R':'S'}])
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

  def overlayTwoCells(self, s, done):
    ''' test the number of seeker edges that cross or are entirely inside done
        ignore edges that touch but do not cross
        transform done into one or more shapes and return them as a list
    '''
    #print(s.box.bounds, done.box.bounds)
    if done.box.equals(s.box): # rectangle t16 
      return []
    # next four tests rectangle t14
    elif done.w.intersects(s.w) and done.e.intersects(s.e) and done.n.disjoint(s.boundary): 
      return [] if done.s.covers(s.n) else self.split(s, done, required=[{'R':'S'}])
    elif done.w.intersects(s.w) and done.e.intersects(s.e): 
      return [] if done.n.covers(s.s) else self.split(s, done, required=[{'R':'N'}])
    elif done.n.intersects(s.n) and done.s.intersects(s.s) and done.e.disjoint(s.boundary):
      return [] if done.w.covers(s.e) else self.split(s, done, required=[{'R':'W'}])
    elif done.n.intersects(s.n) and done.s.intersects(s.s):
      return [] if done.e.covers(s.w) else self.split(s, done, required=[{'R':'E'}])
    # rectangle t6
    elif done.n.crosses(s.e) and done.w.crosses(s.s):
      return self.split(s, done, required=[{'R':'S'}, {'R':'E'}])
      #return self.split(s, done, required=[{'R':'N'}, {'R':'W'}])
      #return self.split(s, done, required=[{'G':'NW'}])
    elif done.n.crosses(s.w) and done.e.crosses(s.s):
      return self.split(s, done, required=[{'G':'NE'}])
    elif done.s.crosses(s.w) and done.e.crosses(s.n): # test 6
      return self.split(s, done, required=[{'R':'E'}, {'R':'W'}])
      #return self.split(s, done, required=[{'G':'SE'}])
    elif done.w.crosses(s.n) and done.s.crosses(s.e):
      return self.split(s, done, required=[{'G':'SW'}])
    # rectangle t5
    elif done.n.crosses(s.e) and done.s.crosses(s.w):
      return self.split(s, done, required=[{'R':'N'}, {'R':'S'}])
    elif done.e.crosses(s.n) and done.w.crosses(s.s): # test 5
      return self.split(s, done, required=[{'R':'E'}, {'R':'W'}])
    # topdown t2 - t5
    elif done.e.crosses(s.n) and done.w.crosses(s.n): # t2
      return self.split(s, done, required=[{'P':'S'}])
    elif done.e.crosses(s.s) and done.w.crosses(s.s): # t3 TODO
      return self.split(s, done, required=[{'P':'N'}])
    elif done.n.crosses(s.e) and done.s.crosses(s.e): # t4
      return self.split(s, done, required=[{'P':'W'}])
    elif done.n.crosses(s.w) and done.s.crosses(s.w): # t5
      return self.split(s, done, required=[{'P':'E'}])
    # topdown t3.1
    elif done.box.within(s.box):                      
      return self.split(s, done, required=[{'G':'NW'}, {'G':'SE'}])
    # print("Err Flatten.overlayTwoCells NO MATCH")
    return []

  def firstPass(self, todo):
    ''' first pass 
        add any shape that does not collide with another
        these are immutable (cannot be split) and similar to "top cells"
    '''
    done = [] # if it works then remove from init
    for x in todo:
      for d in done:
        if self.overlapTwoCells(x, d):
          break
      else:
        done.append(x)
    self.todo = [t for t in todo if t not in done] # copy everything but done into todo
    self.done = done

  # TODO merge this confusingly named func into firstPass. RENAME firstPass findImmutables
  def overlapTwoCells(self, seeker, done):
    print("done")
    print(done.boundary.geom_type) # expect LinearRing
    print(list(done.boundary.coords))   # .geom_type) # expect LinearRing
    print("seeker")
    print(seeker.boundary.geom_type) # expect LinearRing
    print(list(seeker.boundary.coords)) 
    #return done.boundary.overlaps(seeker.boundary)
    return done.boundary.intersects(seeker.boundary)
    #return done.boundary.contains(seeker.boundary)
    #return done.boundary.touches(seeker.boundary)
    #return done.boundary.within(seeker.boundary)

  def cleanCropped(self, cropped):
    ''' remove anything cropped from a seeker that clashes with done
        boundary tests are used instead of box because non-Rectangles are in the loop
    '''
    cleaned = [] # set to avoid duplicates
    clean = True
    for c in cropped:
      for d in self.done:
        if d.boundary.crosses(c.boundary):
          #print(d.label, " x ", c.label) 
          #print(list(c.boundary.xy))
          clean = False
        print(f"c {c.label} d {d.label} YN {clean}") 
      if clean:
        cleaned.append(c)
      clean = True
    print()
    return cleaned

  def expungeInvisibles(self, todo):
    invisibles = []
    x = todo.pop()
    for y in todo:
      if self.sameBoxen(x, y):
        # print(x.label, y.label)
        invisibles.append(x)
    if len(todo):
      self.expungeInvisibles(todo)
    return invisibles

  def cropSeekers(self, seekers):
    ''' compare each Done against each Seeker (a Seeker is neither done nor invisible)
        align the seekers by cropping whenenver Done overlaps
        when seekers are Gnomons they grow in number
    '''
    print(len(self.done))
    print(len(seekers))
    a = []
    for d in self.done:
      for s in seekers:
        #print(f"d {d.label} s {s.label} len {len(shapes)}")
        shapes = self.overlayTwoCells(s, d)
        if len(shapes) == 2: # Gnomons
          [a.append(shape) for shape in shapes]
        elif len(shapes) == 1: # Rectangle or Parabola
          a.append(shapes[0])
    return a


class MinkFlatten():
  ''' tactical flattener that only knows Minkscape
      strategy is Top-N-Tail
      =collect the immutables aka top
      start with empty list done
      iterate through todo and add seeker to done 
      unless seeker overlaps with already done

      remove the invisibles aka background
      split remainder against immutables
      split remainder against themselves
      calculate sum of area to validate results
  '''
  def __init__(self):
    ''' make two lists of rects, todo and done, as exact copies
    '''
    # pos     size     color
    init = [
      [( 0, 0, 30,30), 'CCC'],
      [(30, 0, 30,30), 'CCC'],
      [(60, 0, 30,30), 'CCC'],
      [( 0, 0, 30,30), 'FFF'],
      [(40, 0, 10,30), '000'], 
      [(70,10, 10,10), '000'],
      [(10,10, 10,10), '000'],
      [(20,10, 50,10), 'FFF'] 
    ]
    '''
    self.done = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(init)
    ]
    '''
    self.todo = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(init)
    ]
    self.f = Flatten()


  def findSpace(self, seeker):
    ''' attempt to find a space sought by this shape
    split any that collide and retest
    returning False will cause a rect to be ignored
    '''
    found = []
    #print(seeker.label)
    for d in self.done:
      found = self.f.overlayTwoCells(seeker, d)
      # TODO make sure flatten exludes up from [shapes]
      if len(found): # note: greater than 0 adds unwanted shapes
        #print('numof found ', len(found), 'direction', d)
        #print(f"s {seeker.label} d {d.label} {len(found)}")
        break
    return found


  def _firstPass(self):
    ''' first pass 
        add any shape that does not collide with another
        these are immutable (cannot be split) and similar to "top cells"
    '''
    top = []
    for x in self.done:
      shapes = self.findSpace(x)
      if len(shapes) == 0:
        top.append(x)
    self.done = top
    self.todo = [t for t in self.todo if t not in top]


  def theParabolaHack(self):
    ''' parabolas cannot be added to done 
    because of a fault in collision detection
    this hack forces but only works for minkscape
    '''
    missing = ['PFFF     0  0 30 30', 'PCCC    60  0 30 30']
    for t in self.todo:
      for label in missing:
        if label == t.label:
          self.done.append(t) 

  # TODO look into Shapely.area()
  def checkAreaSum(expected_area, done=list()):
    ''' check the done set() by calculating the bounded area
    the sum of all bounded area should equal blocksize * cellsize
    if higher than fail because there are overlaps
    if lower then warn about unallocated whitespace (run visual check)
    '''
    area = 0
    for s in done:
      print(s.label, area)
      area += s.area()           # TODO Gnomon and Parabole area()
    if area > expected_area:
      #raise ValueError(f"overlapping: expected {expected_area} actual {area}")
      print(f"overlapping: expected {expected_area} actual {area}")
    elif area < expected_area:
      print(f"whitespace warning: expected {expected_area} actual {area}")

  def t(self):
    expected = [
      'PFFF     0  0 30 30',
      'RCCC    30 20 10 10',
      'R000    10 10 10 10',
      'R000    70 10 10 10',
      'RCCC    30  0 10 10',
      'RCCC    50  0 10 10',
      'RCCC    50 20 10 10',
      'R000    40  0 10 10',
      'R000    40 20 10 10',
      'PCCC    60  0 30 30',
      'RFFF    20 10 50 10' 
    ]
    unwanted = [x.label for x in self.done if x.label not in expected]
    done_labels = set([d.label for d in self.done])
    omitted = [e for e in expected if e not in done_labels]
    return unwanted, omitted

  def secondPass(self):
    ''' second pass
    compare the remaining shapes to top 
    shapes that collide are split and added for a subsequent retry
    or without colliding they are added directly
    further splitting may happen on subsequent retries
    but if there none then loop exists before max retries is reached
    '''
    retries = 3

    for rt in range(retries):
      stash = []
      for shape in self.todo:
        collides = self.findSpace(shape)
        if len(collides):
          [stash.append(c) for c in collides]
        else:
          self.done.append(shape)
        print(rt, len(stash), len(self.done))
        [print(s.label) for s in stash]
      else: # retry while there is stuff todo
        self.todo = stash
        #[print(t.label) for t in todo]
        continue

if __name__ == '__main__':
  ''' quick test to make a parabola from two boxen
  '''
  f = Flatten()
  r1 = Rectangle(x=1, y=1, w=6, h=3)
  print(r1.name)
  r2 = Rectangle(x=3, y=2, w=2, h=3)
  shapes = f.overlayTwoCells(r2, r1)
  if len(shapes):
    r1.plotPoints(seeker=shapes[0]) 

