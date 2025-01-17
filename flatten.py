import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon, LinearRing
from cell.geomink import Geomink, Plotter

# TODO
'''
Once all seekers have been tested the surface area of the stencil is returned together with done
Using blocksize and cellsize the expected surface area can be compared to the stencil area.
'''

class Flatten():
  ''' create a stencil as a MultiPolygon and a done list to contain Geomink shapes
      The first seeker will always be added because the stencil starts with a surface area of zero.
  '''
  VERBOSE  = False
  scale    = 1.0
  cellsize = 15

  def __init__(self):
    self.stencil = MultiPolygon([])
    self.stats   = [0, 0, 0, 0, 0] # add merge crop ignore punch
    self.done    = dict()
    # R:6 has label R6 as the sixth rectangle of the block
    self.labels  = dict(zip(['R', 'S', 'G', 'P', 'I'], [0, 0, 0, 0, 0]))
    self.writer  = Plotter()

  def run(self, todo):
    ''' run once for each block
        beware of delicate logic, especially multiple touches!
    '''
    for seeker in todo: 
      events = self.evalSeeker(seeker)
      for outcome in events:
        shape, control = list(outcome.items())[0]
        if control == 4: self.punch(seeker, shape)
        elif control == 3:
          self.stats[3] += 1
          if self.VERBOSE: print(f"seeker ignored {seeker.shape.bounds}")
        elif control == 2: 
          self.crop(seeker, shape)
          break # avoid touching events
        elif control == 1: self.merge(seeker, shape)
        elif control == 0: self.add(seeker)
        else: raise NotImplementedError(control)

  def evalSeeker(self, seeker):
    ''' seeker evaluation can have 5 outcomes

        | control  | transform | touches |
        +----------+-----------+---------+
        | 0 add    | -         | 0       |
        | 1 merge  | -         | 0..n    |
        | 2 crop   | yes       | 1..n    |
        | 3 ignore | -         | 1       |
        | 4 punch  | yes       | 1..n    |
    
        control is an int defining flow
        target  is the geom in the stencil to be used in transforming the seeker
        touches describes the impact of touching shapes stencil updates
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
    return reversed(events)  # reverse to give precedence to the higher order events

  def addSeeker(self, seeker):
    key   = seeker.shape.bounds
    label = seeker.label
    added = False
    if key not in self.done:       # ignore seekers that we saw before
      self.labels[label] += 1
      seeker.label   = f"{label}{self.labels[label]}"
      self.done[key] = seeker
      added = True
    return added

  def punch(self, seeker, shape):
    ''' punch a hole and make a square ring polygon
        merge with stencil whenever addSeeker succeeds
    #self.writer.plot(shape, seeker.shape, fn='S2')
    '''
    diff  = seeker.shape.difference(shape) # the part of shape that differs from seeker
    if diff.is_empty: # treat empties as rectangles and add them
      gmk = Geomink(
        self.scale, self.cellsize, polygon=seeker.shape, pencolor=seeker.pencolor, label='R'
      )
      if self.addSeeker(gmk): self.mpAppend(seeker.shape)
    elif diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        gmk = Geomink(
          self.scale, self.cellsize, polygon=p, pencolor=seeker.pencolor, label=self.identify(p)
        )
        if self.addSeeker(gmk):
          self.stats[4] += 1
          if self.VERBOSE: print(f"{gmk.label} mp punched hole")
    else:
      gmk = Geomink(
        self.scale, self.cellsize, polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff)      )
      if self.addSeeker(gmk):
        self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
        self.mpAppend(diff)
        self.stats[4] += 1
        if self.VERBOSE: print(f"{gmk.label} punched hole")

  def crop(self, seeker, shape):
    ''' crop the seeker by removing areas that overlap shape
    '''
    # before cropping, remove shape from stencil by copying all the others
    diff = seeker.shape.difference(shape) # the part of shape that differs from seeker
    if diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        gmk = Geomink(
          self.scale, self.cellsize, polygon=p, pencolor=seeker.pencolor, label=self.identify(p)
        )
        if self.addSeeker(gmk):
          self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
          shape = shape.union(p)        # merge the remaining part(s) into the stencil
          self.mpAppend(shape)
          self.stats[2] += 1
          if self.VERBOSE: print(f"{gmk.label} mp cropped")
    elif diff.geom_type == 'Polygon':
      gmk = Geomink(
        self.scale, self.cellsize, polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff)      )
      if self.addSeeker(gmk):
        self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
        shape = shape.union(diff)
        self.mpAppend(shape)
        self.stats[2] += 1
        if self.VERBOSE: print(f"{gmk.label} cropped")
    else:
      raise ValueError(f"{diff.geom_type=} was not expected")

  def merge(self, seeker, shape):
    ''' only add seeker once when there are multiple touching events 
        otherwise the seeker will be added to done for each event
    '''
    gmk = Geomink(
      self.scale, self.cellsize, polygon=seeker.shape, pencolor=seeker.pencolor, label='R'
    )
    if self.addSeeker(gmk):
      self.stencil = MultiPolygon([g for g in self.stencil.geoms if not g.equals(shape)])
      stretch = shape.union(seeker.shape)
      self.mpAppend(stretch) # self.mpAppend(seeker.shape)
      self.stats[1] += 1
      if self.VERBOSE: print(f"{gmk.label} merged")
    else:
      pass #if self.VERBOSE: print(f"skipped adding seeker to done {seeker.shape}")

  def add(self, seeker):
    self.mpAppend(seeker.shape)
    gmk = Geomink(
      self.scale, self.cellsize, polygon=seeker.shape, pencolor=seeker.pencolor, label='R'
    )
    self.addSeeker(gmk)
    self.stats[0] += 1
    if self.VERBOSE: print(f"{gmk.label} added")

  def get(self, label):
    gmk = [d for d in self.done.values() if label == d.label]
    if len(gmk) == 1:
      return gmk[0]

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
    elif assertion == 'parabola' and count in [9, 11]: 
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
      pass # if self.VERBOSE: print(f'{assertion} with {count} coords was not found')
    return False

if __name__ == '__main__':
  ''' e2e test to flatten minkscape
      also see t/flatten.py for unit tests
  '''
  f = Flatten()
  data = [
    [(0, 0, 3, 3), 'CCC'],
    [(3, 0, 6, 3), 'CCC'],
    [(6, 0, 9, 3), 'CCC'],
    [(0, 0, 3, 3), 'FFF'],
    [(4, 0, 5, 3), '000'],
    [(7, 1, 8, 2), '000'],
    [(1, 1, 2, 2), '000'],
    [(2, 1, 6, 2), 'FFF']   # original value 2,1,5,1 tweaked for use-case control:0
  ]
  todo = [Geomink(f.scale, f.cellsize, i[0], pencolor=i[1]) for i in reversed(data)]
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
