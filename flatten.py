from shapely.geometry import Polygon
from shapes import Rectangle, Gnomon, Parabola, FakeBox
import pprint
pp = pprint.PrettyPrinter(indent=2)

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
