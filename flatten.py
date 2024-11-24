import sys
import matplotlib.pyplot as plt
import pprint
from shapely.geometry import box, LinearRing, Polygon, LineString
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

  # TODO ClassName functionName var_name
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
      d = (90,405)
    elif self.direction in ['E', 'W']:
      d = (0,360)
    m             = Meander(xywh, direction=d)
    points        = m.collectPoints()
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
      d = (270, 315, 360)
    elif self.direction == 'SE':
      d = (180, 135, 405)
    else:
      raise NotImplementedError(f'all at sea >{self.direction}<')
    '''
    print(xywh)
    print(d)
    '''
    m             = Meander(xywh, direction=d)
    points        = m.collectPoints()
    self.linefill = m.makeStripes(points)

class Parabola(Rectangle):
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  # TODO pass pencol to parent Rectangle()
  def __init__(self, seeker, done, direction):
    super().__init__(name = 'P')
    x, y, w, h = done.box.bounds
    X, Y, W, H = seeker.box.bounds
    self.pencolor = seeker.pencolor
    self.direction = direction
    self.label = f'{self.name}{self.pencolor:<6}{int(X):>3}{int(Y):>3}{int(W):>3}{int(H):>3}'

    if self.direction == 'N':
      self.p2      = Y
      self.start   = X
      self.stop    = W
      self.oddline = H
      self.outer   = Y
      self.inner   = h
      self.boundary = LinearRing([(X,Y), (X,H), (W,H), (W,Y), (w,Y), (w,h), (x,h), (x,Y)])
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
    if self.direction == 'W': 
      gnomon_d   = (450,135,90)
      rectangl_d = (495,270)
    elif self.direction == 'E': 
      gnomon_d   = (180,225,270)
      rectangl_d = (180,450)
    else:
      raise NotImplementedError(f'all at sea >{self.direction}<')
    '''
    print(f"""
{self.direction=} 
{self.gnomon=} 
{gnomon_d=} 
{self.rectangl=} 
{rectangl_d=}
""") 
    '''
    g  = Meander(self.gnomon,   direction=gnomon_d)
    r  = Meander(self.rectangl, direction=rectangl_d)
    p1 = g.collectPoints()
    p2 = r.collectPoints()

    self.linefill = r.joinStripes(p1, p2)

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


class Flatten:

  def __init__(self):
    self.done    = []      # immutable shapes
    self.todo    = []      # shapes that are not yet done are called seekers
    self.merge_d = []      # top shapes are merged into this list
    self.found   = dict()  # stash shapes found by self.cmpSeekers()

  def combine(self, polygon, pencolor):
    ''' return a Rectangle without checkng what Shapely.difference produced
    '''
    #print(polygon.bounds, seeker.label)
    x, y, w, h = polygon.bounds
    w -= x  # TODO refactor so that Rectangle can accept bounds
    h -= y
    return Rectangle(pencolor=pencolor, x=x, y=y, w=w, h=h)

  def assemble(self, seekers):
    ''' reunite found with seekers
    '''
    #print(f"{len(seekers)=}")
    for label in self.found:
      mp = self.found[label]
      #print(f"{label} {len(mp.geoms)}")
      ''' identify and destroy the covering shape
      '''
      delete_me = None
      pencolor = None
      #print(f"{s.pencolor=}")
      for i, s in enumerate(seekers):
        if s.label == label:
          delete_me = i
          pencolor = s.pencolor
          break
      if delete_me:
        del seekers[delete_me] # about to be replaced 
      ''' combine the color with the new shape
      '''
      for p in mp.geoms:
        r = self.combine(p, pencolor)
        seekers.append(r)
    return seekers 

  def cmpSeekers(self, seekers):
    ''' collision detect seekers against each other
        stash new shapes in Flatten and their index
        after comparison replace old with new using index
    '''
    this = seekers.pop()
    p = Polygon(this.boundary)
    for s in seekers: 
      seeker = Polygon(s.boundary)
      if p.covers(seeker):
        multipolygon = p.difference(seeker) # like self.split but better
        #print(f"{this.label} {this.pencolor} | {s.label} {this.name} {this.direction}")
        if multipolygon.is_empty:
          pass # should not happen
        else:
          self.found[this.label] = multipolygon
    if len(seekers):
      self.cmpSeekers(seekers)
    return None

  def sameBoxen(self, seeker, done):
    return seeker.box.equals(done.box)

  def split(self, seeker, done, required=list()):
    shapes = []
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
          s.setSeeker(seeker, direction)   # transform done copy into seeker
          x, y, w, h = s.dimensions()       # get the new values
          s.setDimensions(
            {'x':x, 'y':y, 'w':w, 'h':h}, 
            direction=direction, 
            pencolor=seeker.pencolor
          ) # apply for meander
        else:
          raise ValueError(f"cannot split anonymous '{name}'")
        shapes.append(s)
    return shapes

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
    #print("Err Flatten.overlayTwoCells NO MATCH")
    return []

  # TODO merge this confusingly named func into firstPass. RENAME firstPass findImmutables
  def overlapTwoCells(self, seeker, done):
    '''
    '''
    return done.boundary.crosses(seeker.boundary)

  def expungeInvisibles(self, todo):
    invisibles = [] # TODO test this with more than a single invisible
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
    #print(f"{len(self.done)=} {len(seekers)=}")
    a = [] 
    for d in self.merge_d:
      for s in seekers:
        #print(f"{s.label=}")
        shapes = self.overlayTwoCells(s, d)
        if len(shapes) == 2: # Gnomons
          [a.append(shape) for shape in shapes]
          '''
          for shape in shapes:
            #print(f"{shape.label=}")
            if shape.label == 'R000     4  2  5  3':
              shape.meander()
              xy = list(shape.linefill.coords)
              #print(xy)
          '''
        elif len(shapes) == 1: # Rectangle or Parabola
          a.append(shapes[0])
    return a

  def mergeDone(self, done):
    ''' assume we get Polygons and if they touch then merge them
        shapes that touch more than once get added twice
    '''
    last = done.pop()
    for d in done:
      if last.box.intersects(d.box):
        #print(f"{d.box.geom_type=} {d.label=} {last.label=}")
        if hasattr(self, 'merge_d'):
          p  = last.box.union(d.box) # shapely gives us a merged polygon
          fb = FakeBox(p)            # rectanglify
          self.merge_d.append(fb)
        else:
          p  = last.box.union(d.box) # shapely gives us a merged polygon
          fb = FakeBox(p)            # rectanglify
          self.merge_d.append(fb)
    if len(done):
      self.mergeDone(done)
    return None

  def firstPass(self, todo):
    ''' first pass 
        add any shape that does not collide with another
        these are immutable (cannot be split) and similar to "top cells"
    '''
    done = [] 
    for x in todo:
      for d in done:
        if self.overlapTwoCells(x, d):
          break
      else:
        done.append(x)
    self.todo = [t for t in todo if t not in done] # copy everything but done into todo
    self.done = done

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

  def run(self, todo):
    ''' orchestrate Flattening from here. There are five steps
        1. isolate the top cells as self.done
        2. remove invisible cells, e.g. background covered by square
        3. merge the done into a template for cropping seeker
        4. crop the seekers
        5. re-assemble the parts
    '''
    self.firstPass(todo)               # create Flatten().done
    #print(f"{len(self.todo)=}")
    todo = [x for x in self.todo]      # make a hard copy
    invisibles = self.expungeInvisibles(todo)
    self.todo = [x for x in self.todo if x not in invisibles] # omit the invisibles
    done  = self.done[:]               # another copy
    count = len(done)
    self.mergeDone(done)            # should set two merged Polygons in Flatten
    if count > len(self.merge_d):   # if something merged then check again
      done = self.merge_d[:]        # hard copy
      self.merge_d = []      
      self.mergeDone(done)          # compare two merged Polygons with each other
      #[print(p.box.bounds) for p in self.merge_d]
    seekers = self.cropSeekers(self.todo)
    ''' debug
    for s in seekers:
      if s.label == 'R000     4  2  5  3':
        s.meander()
        xy = list(s.linefill.coords)
        print(xy)
    '''
    tmp = seekers[:]
    self.cmpSeekers(tmp)        # after comparison any that overlap are saved in Flatten.found
    seekers = self.assemble(seekers)   # new seekers but not the folk singers :-)
    self.done.extend(seekers)          # not the folk singers :-)
    return self.done
    '''
    PFFF     0  0  3  3
    PCCC     6  0  9  3
    R000     4  2  5  3  meander empty
    R000     4  0  5  1  meander empty
    RCCC     3  0  4  1
    RCCC     5  0  6  1
    RCCC     3  2  4  3
    RCCC     5  2  6  3
    RFFF     2  1  7  2
    R000     1  1  2  2
    R000     7  1  8  2
    '''

if __name__ == '__main__':
  ''' test to flatten minkscape
  '''
  f = Flatten()
  data = [
    [(0, 0, 3, 3), 'CCC'],
    [(3, 0, 3, 3), 'CCC'],
    [(6, 0, 3, 3), 'CCC'],
    [(0, 0, 3, 3), 'FFF'],
    [(4, 0, 1, 3), '000'],
    [(7, 1, 1, 1), '000'],
    [(1, 1, 1, 1), '000'],
    [(2, 1, 5, 1), 'FFF'] 
  ]
  todo = [
    Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(data)
  ]
  #[print(t.label) for t in todo]
  f.run(todo)
'''
the
end
'''
