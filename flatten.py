import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon, LinearRing
from shapes import Geomink, Plotter

# TODO
'''
Once all seekers have been tested the surface area of the stencil is returned together with done
Using blocksize and cellsize the expected surface area can be compared to the stencil area.
'''

class Flatten():
  ''' create a stencil as a MultiPolygon and a done list to contain Geomink shapes
      The first seeker will always be added because the stencil starts with a surface area of zero.
  '''
  VERBOSE = False

  def __init__(self):
    self.stencil = MultiPolygon([])
    self.stats   = [0, 0, 0, 0, 0] # add merge crop ignore punch
    self.done    = dict()
    # R:6 has label R6 as the sixth rectangle of the block
    self.labels  = dict(zip(['R', 'S', 'G', 'P', 'I'], [1, 1, 1, 1, 1]))
    self.writer  = Plotter()

  def run(self, todo):
    ''' run once for each block
    print(f"{len(self.stencil.geoms)=}")
    #print('.', end='', flush=True)
    #self.writer.plot(self.stencil.geoms[0], todo[16].shape, fn='koto_done')
      first      = False
      if multitouch:
        del events[-1:]  # chop all but the last
          if multitouch and first:
            pass
          else:
            first = True
      print('.'*100)
    svgfile = f"koto_stencil_{len(self.stencil.geoms)}"
    self.writer.multiPlot(self.stencil, fn=svgfile)
    '''
    for seeker in todo[:]:  # 17 is when S3 background appears, see note.txt
      events     = self.evalSeeker(seeker)
      multitouch = True if len(events) > 1 else False
      for outcome in events:
        shape, covering = list(outcome.items())[0]
        #print(f"{covering=}", shape)
        if covering == 5: self.multiMerge(seeker, shape)
        elif covering == 4: self.punch(seeker, shape)
        elif covering == 3:
          self.stats[3] += 1
          if self.VERBOSE: print(f"seeker ignored {seeker.shape.bounds}")
        elif covering == 2: self.crop(seeker, shape)
        elif covering == 1: self.merge(seeker, shape, skip=False)
        elif covering == 0: self.add(seeker)
        else: raise NotImplementedError(covering)

  def evalSeeker(self, seeker):
    ''' seeker evaluation can have 4 outcomes
      4. stencil is completely within seeker
      3. stencil completely covers seeker THEN ignore the seeker and report a miss
         OR stencil almost covers seeker, but one or more borders are aligned THEN as above
      2. stencil overlaps (partially covers) seeker THEN
          a. crop seeker and throw away the covered part
          b. extend the stencil to include the remainder
          c. add the remaining part to the done list
      1. stencil touches the seeker but does not cover THEN
          a. extend the stencil shape that touched to include the seeker
          b. add the seeker to the done list
      0. stencil neither covers nor touches the seeker THEN
          a. add new shape to the stencil
          b. add the seeker to the done list
    '''
    events = []
    for shape in self.stencil.geoms:
      e = 0
      if shape.within(seeker.shape):    e = 4
      elif shape.covers(seeker.shape):  e = 3
      elif shape.overlaps(seeker.shape):e = 2
      elif shape.touches(seeker.shape): e = 1
      if e:
        events.append({shape:e})
    if not len(events): # primer for first run
      events.append({None:0})
    return events

  def addSeeker(self, seeker):
    key   = seeker.shape.bounds
    label = seeker.label
    if key not in self.done:       # ignore seekers that we saw before
      self.labels[label] += 1
    seeker.label   = f"{label}{self.labels[label]}"
    self.done[key] = seeker

  def punch(self, seeker, shape):
    ''' punch a hole and make a square ring polygon
    '''
    diff  = seeker.shape.difference(shape) # the part of shape that differs from seeker
    #self.writer.plot(shape, seeker.shape, fn='S1')
    if diff.is_empty: # treat empties as rectangles and add them
      gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label='R')
      self.addSeeker(gmk)
    elif diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        gmk = Geomink(polygon=p, pencolor=seeker.pencolor, label=self.identify(p))
        self.addSeeker(gmk)
    else:
      gmk = Geomink(polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff))
      self.addSeeker(gmk)
      # TODO how is it going to work for MultiPolygon ?
      self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
      self.mpAppend(seeker.shape)
    self.stats[4] += 1
    if self.VERBOSE: print(f"{gmk.label} punched hole")

  def crop(self, seeker, shape):
    ''' crop the seeker by removing areas that overlap shape
    '''
    # before cropping, remove shape from stencil by copying all the others
    self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
    diff = seeker.shape.difference(shape) # the part of shape that differs from seeker
    if diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        gmk   = Geomink(polygon=p, pencolor=seeker.pencolor, label=self.identify(p))
        self.addSeeker(gmk)
        shape = shape.union(p)        # merge the remaining part(s) into the stencil
        self.stats[2] += 1
        if self.VERBOSE: print(f"{gmk.label} cropped")
    elif diff.geom_type == 'Polygon':
      gmk   = Geomink(polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff))
      self.addSeeker(gmk)
      shape = shape.union(diff)
      self.stats[2] += 1
      if self.VERBOSE: print(f"{gmk.label} cropped")
    else:
      raise ValueError(f"{diff.geom_type=} was not expected")
    self.mpAppend(shape)

  def merge(self, seeker, shape, skip=False):
    ''' only add seeker once when there are multiple touching events 
        otherwise the seeker will be added to done for each event
    '''
    if skip:
      if self.VERBOSE: print(f"skipped adding seeker to done {seeker.shape}")
    else:
      self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
      stretch = shape.union(seeker.shape)
      self.mpAppend(stretch)
      '''
      self.mpAppend(seeker.shape)
      '''
      gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label='R')
      self.addSeeker(gmk)
      self.stats[1] += 1
      if self.VERBOSE: print(f"{gmk.label} merged")

  def add(self, seeker):
    self.mpAppend(seeker.shape)
    gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label='R')
    self.addSeeker(gmk)
    self.stats[0] += 1
    if self.VERBOSE: print(f"{gmk.label} added")

  def mpMerge(self, mp):
    ''' merge them what touch
    print(f"{remain=}")
    print(f"{merged=}")
    print(f"{m.geom_type=}")
    '''
    merged = list()
    purged = list()
    n      = len(mp)
    for p1 in reversed(mp):
      n -= 1
      for p2 in mp[:n]:
        if p1.touches(p2):
          m = p1.union(p2)
          [merged.append(p) for p in self.mpList(m)]
          purged.append(p1)
          purged.append(p2)
    remain = [p for p in mp if p not in purged]
    return merged + remain

  def mpList(self, strange):
    ''' some Geometry operations return scalars others collections
        this function guarentees to return a list
    '''
    mp = list()
    if strange.geom_type == 'Polygon':
      mp.append(strange)
    elif strange.geom_type == 'MultiPolygon':
      [mp.append(p) for p in strange.geoms]
    else:
      raise TypeError(f"{strange} what are you?")
    return mp

  def mpAppend(self, new_polygon):
    ''' MultiPolygon is a GeometrySequence that validates its members
        provide an append function by converting to list before adding new
    '''
    old_mp = [p for p in self.stencil.geoms]
    new_mp = self.mpList(new_polygon)
    '''
    if new_polygon.geom_type == 'Polygon':
      mp.append(new_polygon)
    elif new_polygon.geom_type == 'MultiPolygon':
      [mp.append(p) for p in new_polygon.geoms]
    else:
      raise TypeError(f"{new_polygon} what are you?")
    '''
    mp = old_mp + new_mp # causing timeout self.mpMerge(old_mp + new_mp)
    self.stencil = MultiPolygon(mp)

  def identify(self, shape):
    ''' attempt to identify a shape that Meander.fill can handle 
        default to Irregular if none 
    '''
    if shape.geom_type == 'MultiPolygon':
      raise TypeError(f'cannot identify {shape.geom_type}')

    if self.shapeTeller(shape, 'rectangle'):
      label = 'R'
    elif self.shapeTeller(shape, 'gnomon'):
      label = 'G'
    elif self.shapeTeller(shape, 'parabola'):
      label = 'P'
    elif self.shapeTeller(shape, 'sqring'):
      label   = 'S'
    else:  # raise TypeError(f'unidentified {shape.geom_type}')
      label = 'I'   
    #return self.stickLabel(label)
    return label

  def stickLabel(self, label):
    if label in self.labels:
      self.labels[label] += 1
    else:
      self.labels[label] = 1
    return f"{label}{self.labels[label]}"

  def shapeTeller(self, shape, assertion):
    ''' count the points and decide if the asserted shape is correct

        parabolas have shallow or deep ingress
        should split 9 and 11 into Parabola.small and Large?
        13 is a spade with danglers

        simplify was not helpful 
        clean = self.shape.exterior.simplify(tolerance=1, preserve_topology=True)
    '''
    count = 0

    outer = list(shape.exterior.coords)
    inner = list(shape.interiors)
    if len(inner) > 1:
      raise NotImplementedError(assertion)
    elif len(inner) == 1:  # multi part geometry
      count = len(outer) + len(inner[0].coords)
    else: # only the single part geometries are cleaned .. 
      count = len(outer)

    if assertion == 'rectangle' and count in [5, 6]: # 6 is for danglers
      return True
    elif assertion == 'gnomon' and count in [7, 8]:
      return True
    elif assertion == 'parabola' and count == 9: #in [9, 11, 12, 13]: 
      x, y, w, h = shape.bounds
      width      = w - x
      height     = h - y
      if shape.is_valid:
        if width == height:
          if not width % 3:
            return True
          else:
            if self.VERBOSE: print(f"""{assertion} indivisible by 3 {width=}""")
        else:
          if self.VERBOSE: print(f"""{assertion} not a square {width} {height}""")
      else:
        if self.VERBOSE: print(f"""{assertion} is not a valid polygon {x=} {y=} {w=} {h=}""")
    elif assertion == 'sqring' and count == 10:
      return True
    else:
      pass
      # if self.VERBOSE: print(f'{assertion} with {count} coords was not found')
    return False

  def ZZevalSeeker(self, seeker):
    ''' seeker evaluation can have 4 outcomes
      4. stencil is completely within seeker
      3. stencil completely covers seeker THEN ignore the seeker and report a miss
         OR stencil almost covers seeker, but one or more borders are aligned THEN as above
      2. stencil overlaps (partially covers) seeker THEN
          a. crop seeker and throw away the covered part
          b. extend the stencil to include the remainder
          c. add the remaining part to the done list
      1. stencil touches the seeker but does not cover THEN
          a. extend the stencil shape that touched to include the seeker
          b. add the seeker to the done list
      0. stencil neither covers nor touches the seeker THEN
          a. add new shape to the stencil
          b. add the seeker to the done list
    '''
    covering = 0
    touching = []
    for shape in self.stencil.geoms:
      if shape.within(seeker.shape):
        covering = 4
        touching.append(shape)
      elif shape.covers(seeker.shape):
        covering = 3
      elif shape.overlaps(seeker.shape):
        covering = 2
        touching.append(shape)
        # remove shape from stencil by copying all the others
        self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
      elif shape.touches(seeker.shape):
        covering = 1
        touching.append(shape)
        self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])

    if len(touching) > 1: # with multiple touches all shapes must be added to stencil
      #covering = 5
      #shape = touching
      shape = touching[-1]
    elif len(touching) == 1:
      shape = touching[0] # first touch
    else:
      shape = None
    return covering, shape

  def ZZrun(self, todo):
    ''' run once for each block
    '''
    for seeker in todo[:5]:
      covering, shape = self.evalSeeker(seeker)
      if covering == 5: self.multiMerge(seeker, shape)
      elif covering == 4: self.punch(seeker, shape)
      elif covering == 3:
        self.stats[3] += 1
        if self.VERBOSE: print(f"seeker ignored")
      elif covering == 2: self.crop(seeker, shape)
      elif covering == 1: self.merge(seeker, shape)
      elif covering == 0: self.add(seeker)
      else: raise NotImplementedError(covering)
    #print('.', end='', flush=True)
    self.writer.plot(self.stencil.geoms[0], todo[4].shape, fn='koto_done')
    print(f"{len(self.stencil.geoms)=}")
    if len(self.stencil.geoms) > 1:
      self.writer.plot(self.stencil.geoms[0], self.stencil.geoms[1], fn='koto_stencil')

if __name__ == '__main__':
  ''' e2e test to flatten minkscape
      also see t/flatten.py for unit tests
  # TODO remove
  def multiMerge(self, seeker, shapes):
    stretch = shapes[0].union(seeker.shape)
    for shape in shapes[1:]:
      stretch = stretch.union(shape)
    self.mpAppend(stretch)
    gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label=self.stickLabel('R'))
    self.addSeeker(gmk)
    self.stats[1] += 1
    if self.VERBOSE: print(f"{gmk.label} multi-merged")

    [(0, 0, 3, 3), 'CCC'],
    [(3, 0, 6, 3), 'CCC'],
    [(6, 0, 9, 3), 'CCC'],
    [(0, 0, 3, 3), 'FFF'],
    [(4, 0, 5, 3), '000'],
    [(7, 1, 8, 2), '000'],
    [(1, 1, 2, 2), '000'],
    [(2, 1, 6, 2), 'FFF']   # original value 2,1,5,1 tweaked for use-case covering:0
  '''
  f = Flatten()
  data = [
    [(45, 0, 60, 15),  'FFF'],
    [(30, 15, 45, 30), 'FFF'],
    [(30, 0, 45, 15),  'FFF'],
    [(45, 15, 60, 30), 'FFF'],
    [(60, 0, 75, 15),  'FFF'],
    [(75, 0, 90, 15),  'FFF'],
    [(60, 15, 75, 30), 'FFF'],
    [(75, 15, 90, 30), 'FFF'],
    [(0, 0, 15, 15),   'FFF'],
    [(15, 0, 30, 15),  'FFF'],
    [(0, 15, 15, 30),  'FFF'],
    [(15, 15, 30, 30), 'FFF'],
    [(45, 5, 60, 10),  'FFA500'],
    [(30, 20, 45, 25), 'FFA500'],
    [(30, 5, 45, 10),  '4B0082'],
    [(45, 20, 60, 25), '4B0082'],
    [(60, 0, 75, 15),  'FFA500'],
    [(75, 0, 90, 15),  'FFA500'],
    [(60, 15, 75, 30), 'FFA500'],
    [(75, 15, 90, 30), 'FFA500'],
    [(8, 8, 13, 13),   'FFA500'],
    [(24, 10, 29, 15), '4B0082'],
    [(0, 15, 15, 30),  '4B0082'],
    [(15, 15, 30, 30), 'FFA500'],
    [(8, 24, 13, 29),  'FFA500'],
    [(24, 24, 29, 29), '4B0082'],
    [(0, 0, 15, 15),   '4B0082'],
    [(15, 0, 30, 15),  'FFA500']
  ]
  todo = [Geomink(i[0], pencolor=i[1]) for i in reversed(data)]
  f.run(todo)
  print('='*80)
  print(f"""
add {f.stats[0]} merge {f.stats[1]} crop {f.stats[2]} ignore {f.stats[3]} punch {f.stats[4]}
""")
  print(f"TOTAL {len(f.done)=}")

'''
the
end
'''

