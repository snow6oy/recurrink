import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon, LinearRing
from shapes import Geomink

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
    self.done    = []
    self.labels  = dict()  # e.g. R:6 has label R06 as the sixth rectangle of the block

  def run(self, todo):
    #print(len(todo)) 66
    for seeker in todo:
      covering, shape = self.evalSeeker(seeker)
      if covering == 5: self.multiMerge(seeker, shape)
      elif covering == 4: self.punch(seeker, shape)
      elif covering == 3:
        if self.VERBOSE: print(f"seeker ignored")
      elif covering == 2: self.crop(seeker, shape)
      elif covering == 1: self.merge(seeker, shape)
      elif covering == 0: self.add(seeker)
      else: raise NotImplementedError(covering)
    print('.', end='', flush=True)

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
    self.stats[covering] += 1

    if len(touching) > 1: # with multiple touches all shapes must be added to stencil
      covering = 5
      shape = touching
    elif len(touching) == 1:
      shape = touching[0] # first touch
    else:
      shape = None
    return covering, shape

  def punch(self, seeker, shape):
    ''' punch a hole and make a square ring polygon
    '''
    diff  = seeker.shape.difference(shape) # the part of shape that differs from seeker
    if diff.is_empty: # treat empties as rectangles and add them
      gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label=self.stickLabel('R'))
      self.done.append(gmk)
    elif diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        gmk  = Geomink(polygon=p, pencolor=seeker.pencolor, label=self.identify(p))
        self.done.append(gmk)
    else:
      gmk  = Geomink(polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff))
      self.done.append(gmk)
    if self.VERBOSE: print(f"{gmk.label} punched hole")

  def crop(self, seeker, shape):
    ''' crop the seeker by removing areas that overlap shape
    '''
    diff = seeker.shape.difference(shape) # the part of shape that differs from seeker
    if diff.geom_type == 'MultiPolygon':
      for p in diff.geoms:
        shape = shape.union(p)        # merge the remaining part(s) into the stencil
        gmk   = Geomink(polygon=p, pencolor=seeker.pencolor, label=self.identify(p))
        self.done.append(gmk)
    elif diff.geom_type == 'Polygon':
      gmk   = Geomink(polygon=diff, pencolor=seeker.pencolor, label=self.identify(diff))
      self.done.append(gmk)
      shape = shape.union(diff)
    else:
      raise ValueError(f"{diff.geom_type=} was not expected")
    self.mpAppend(shape)
    if self.VERBOSE: print(f"{gmk.label} cropped")

  def merge(self, seeker, shape):
    stretch = shape.union(seeker.shape)
    self.mpAppend(stretch)
    gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label=self.stickLabel('R'))
    self.done.append(gmk)
    if self.VERBOSE: print(f"{gmk.label} merged")

  def multiMerge(self, seeker, shapes):
    stretch = shapes[0].union(seeker.shape)
    for shape in shapes[1:]:
      stretch = stretch.union(shape)
    self.mpAppend(stretch)
    gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label=self.stickLabel('R'))
    self.done.append(gmk)
    if self.VERBOSE: print(f"{gmk.label} merged")

  def add(self, seeker):
    self.mpAppend(seeker.shape)
    gmk = Geomink(polygon=seeker.shape, pencolor=seeker.pencolor, label=self.stickLabel('R'))
    self.done.append(gmk)
    if self.VERBOSE: print(f"{gmk.label} added")

  def mpAppend(self, new_polygon):
    ''' MultiPolygon is a GeometrySequence that validates its members
        provide an append function by converting to list before adding new
    '''
    mp  = [p for p in self.stencil.geoms]
    if new_polygon.geom_type == 'Polygon':
      mp.append(new_polygon)
    elif new_polygon.geom_type == 'MultiPolygon':
      [mp.append(p) for p in new_polygon.geoms]
    else:
      raise ValueError(f"{new_polygon} what are you?")
    self.stencil = MultiPolygon(mp)

  def identify(self, shape):
    if shape.geom_type == 'MultiPolygon':
      raise ValueError(f'cannot identify {shape.geom_type}')

    if self.shapeTeller(shape, 'rectangle'):
      label   = 'R'
    elif self.shapeTeller(shape, 'gnomon'):
      label   = 'G'
    elif self.shapeTeller(shape, 'parabola'):
      label   = 'P'
    elif self.shapeTeller(shape, 'sqring'):
      label   = 'S'
    else:
      raise ValueError(f'unidentified {shape.geom_type}')
    return self.stickLabel(label)

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

    """{assertion=} {count=} {outer=} {inner=}"""
    if assertion == 'rectangle' and count in [5, 6]: # 6 is for danglers
      return True
    elif assertion == 'gnomon' and count in [7, 8]:
      return True
    elif assertion == 'parabola' and count in [9, 11, 12, 13]: 
      return True
    elif count == 10 and assertion == 'sqring':
      return True
    else:
      if self.VERBOSE: 
        print(f'{assertion} has {count} coords')
        print(f"""
{outer=}
{inner=}""")
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
    [(2, 1, 6, 2), 'FFF']   # original value 2,1,5,1 tweaked for use-case covering:0
  ]
  todo = [Geomink(i[0], pencolor=i[1]) for i in reversed(data)]
  f.run(todo[:5])
  print('='*80)
  print(f"""
add {f.stats[0]} merge {f.stats[1]} crop {f.stats[2]} ignore {f.stats[3]} punch {f.stats[4]}
""")
  print(f"TOTAL {len(f.done)=}")
'''
the
end
'''
