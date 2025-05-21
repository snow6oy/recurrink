from .shape import Shape
from shapely.geometry import LineString

class Identify:

  VERBOSE = False

  # TODO Triangl, Diamond, Circle, SquareRing and Irregular
  def direct(self, name, shape):
    ''' inspect the shape yet-to-be-made and determine a cardinal direction
        and in some cases rename
    '''
    x, y, w, h = shape.bounds
    left       = LineString([(x, y),(x, h)])
    top        = LineString([(x, h),(w, h)])
    right      = LineString([(w, h),(w, y)])
    bottom     = LineString([(x, y),(w, y)])
    if name == 'rectangle' and w - x == h - y:
      facing = 'all'
      name   = 'square'
    elif h - y > w - x:
      facing = 'north'
      name   = 'line'
    elif w - x > h - y:
      facing = 'east'
      name   = 'line'
    elif name == 'gnomon':
      if shape.covers(left) and shape.covers(top):
        facing = 'NW'
      elif shape.covers(right) and shape.covers(bottom):
        facing = 'SE'
      else:
        raise NotImplementedError('gnomon has to face somewhere')
    elif name == 'parabola':
      if shape.covers(left) and shape.covers(top) and shape.covers(right):
        facing = 'north'
      elif shape.covers(right) and shape.covers(top) and shape.covers(bottom):
        facing = 'east'
      elif shape.covers(left) and shape.covers(bottom) and shape.covers(right):
        facing = 'south'
      else:
        facing = 'west'
    elif name == 'sqring':
      facing = 'all'
    else:
      raise NotImplementedError(f'{name} has to face somewhere')
    return name, facing

  def bless(self, shape):
    ''' attempt to identify a shape that Meander.fill can handle 
        default to Irregular if none 
    '''
    if shape.geom_type in ['MultiPolygon','LinearRing']:
      raise NotImplementedError(f'cannot identify {shape.geom_type}')
    if self.shapeTeller(shape, 'rectangle'):
      name = 'rectangle'  # can change to square or line after self.direct
    elif self.shapeTeller(shape, 'gnomon'):
      name = 'gnomon'
    elif self.shapeTeller(shape, 'parabola'):
      name = 'parabola' 
    elif self.shapeTeller(shape, 'sqring'):
      name   = 'sqring'
    else:
      name = 'irregular'   
    return name

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
          if self.VERBOSE: print(f"""{assertion} not square {width} {height}""")
      else:
        if self.VERBOSE: print(f"""
{assertion} is not a valid polygon {x=} {y=} {w=} {h=}""")
    elif assertion == 'sqring' and count == 10:
      return True
    elif self.VERBOSE: print(f'{assertion} with {count} coords was not found')
    return False

class CellMaker(Identify):

  VERBOSE = False
 
  def __init__(self, pos, clen):
    ''' TODO 
        pos  default (0,0)
        clen default to 60
    '''
    self.x    = int(pos[0] * clen)
    self.y    = int(pos[1] * clen)
    self.clen = clen
    self.bft  = list() # b0 background f1 foreground t2 top

  def background(self, label, cell):
    ''' basic square with colour
    '''
    bg_cell = { 
      'shape':'square', 'fill':cell['bg'], 'fill_opacity':1, 
      'size':'medium', 'facing':'all'
    }
    bg = Shape(label, bg_cell)
    bg.draw(self.x, self.y, self.clen)
    self.bft.append(bg)

  def foreground(self, label, cell=dict()):
    fg = Shape(label, cell)
    sw = fg.stroke['width'] if fg.stroke else 0
    fg.draw(self.x, self.y, self.clen)
    #, swidth=sw, size=fg.size, facing=fg.facing print(fg.this.data.bounds)
    self.bft.append(fg)

  def top(self, label, cell):
    ''' alias for clarity
    '''
    self.foreground(label, cell)

  ''' override size with a custom dimension
  def box(self, width_height):
    conf = { 'shape': None, 'fill': 'FFF', 'fill_opacity': 1 }
    w, h = width_height
    box  = Shape('Z', conf) # TODO align label naming with cell naming
    box.this.make(self.x, self.y, w, h)
    return box
  Made this to help Geomink transition .. not sure it will be used
  '''

  def void(self, label, shape):
    ''' place for danglers to hang
    '''
    void = Shape(label, { 'shape': 'void' })
    void.compute(shape)
    self.bft.append(void)

  def getStyle(self, i, linear=False): # layer index
    ''' construct a CSS style 
    '''
    if linear: # get ready to plot
      if 'FFF' in self.bft[i].fill: self.bft[i].fill = '555' # avoid white/white
      style = f"fill:none;stroke:#{self.bft[i].fill};stroke-width:0.5"
      #style = f"fill:none;stroke:#000;stroke-width:1"
    elif i == 0: # force stroke width zero to hide cracks between backgrounds
      style = f"fill:#{self.bft[0].fill};stroke-width:0" 
    else:
      style = (f"fill:#{self.bft[i].fill};" +
        f"fill-opacity:{self.bft[i].opacity}")
      if self.bft[i].stroke:
        style += (f";stroke:#{self.bft[i].stroke['fill']};" +
          f"stroke-width:{self.bft[i].stroke['width']};" +
          f"stroke-dasharray:{self.bft[i].stroke['dasharray']};" +
          f"stroke-opacity:{self.bft[i].stroke['opacity']}")
    return style

  def flatten(self):
    ''' control how done and seeker are evaluated
        done   | seeker |
       --------+--------+
             3 | 2 1 0  | dangler > *
             2 |   1 0  |     top > fg, bg
             1 |     0  |      fg > bg
    '''
    # top bigger than fg, see t.cellmaker.Test.test_p
    if (len(self.bft) > 2 and 
      self.bft[2].this.data.covers(self.bft[1].this.data)): 
      self.bft[1], self.bft[2] = self.bft[2], self.bft[1]

    if len(self.bft) == 4:
      self.bft[2] = self.evalSeeker(self.bft[3], self.bft[2])
      self.bft[1] = self.evalSeeker(self.bft[3], self.bft[1])
      self.bft[0] = self.evalSeeker(self.bft[3], self.bft[0])
      self.bft[1] = self.evalSeeker(self.bft[2], self.bft[1])
      self.bft[0] = self.evalSeeker(self.bft[2], self.bft[0])
    elif len(self.bft) == 3:
      self.bft[1] = self.evalSeeker(self.bft[2], self.bft[1])
      self.bft[0] = self.evalSeeker(self.bft[2], self.bft[0])
    self.bft[0] = self.evalSeeker(self.bft[1], self.bft[0])
    if self.VERBOSE: print(f"{self.bft[0].this.name=}")

  def evalSeeker(self, done, seek):
    ''' done are immutable and already cell members
        seekers may be included, depends on what overlaps with done
        return seeker either modified, emptied or as-is
    ''' 
    #done, seek = self.sortByArea([done, seek])
    if self.VERBOSE: 
      print(f"""
{len(self.bft)=} 
{done.this.name=} {done.this.data.bounds}
{seek.this.name=} {seek.this.data.bounds}""")
    if done.this.data.equals(seek.this.data) or seek.this.data is None:
      seek.this.data = None
      seek.this.name = 'invisible' # fg completely covers bg or was empty
    else:     # if done.this.data.crosses(seek.this.data): 
      diff = seek.this.data.difference(done.this.data, grid_size=1)
      if self.VERBOSE: print(f"{done.label=} {seek.this.name=} {diff}")
      if diff.is_empty:   # nothing overlapped
        pass              # return seek as it came
      elif diff.equals(seek.this.data):
        pass # return seek unchanged
      else:  # deal with the multi geoms later
        if diff.geom_type == 'MultiPolygon':
          seek.this.name = 'multipolygon'
          seek.this.data = diff
        else:
          rename    = self.bless(diff)           # first attempt
          rename, f = self.direct(rename, diff)  # final name
          conf      = {'shape':rename, 'fill':seek.fill, 'facing':f}
          seek      = Shape(seek.label, conf)
          seek.compute(diff)
    return seek

  def sortByArea(self, unordered):
    ''' large then medium then small
    '''
    return sorted(unordered, key=lambda layer: layer.this.data.area, reverse=True)
    #  self.bft, key=lambda layer: layer.this.data.area, reverse=True

  def areaSum(self):
    ''' use shapely area to check flatten coverage
    '''
    expected_area = self.clen * self.clen
    total_area = 0
    if self.VERBOSE: print(f"{expected_area=}")
    for layer in self.bft:
      shape = layer.this
      if shape.name == 'invisible':
        if self.VERBOSE: print(f"{layer.label} {shape.name} omitted")
        continue
      elif shape.name == 'void':
        if self.VERBOSE: 
          print(f"{layer.label} {shape.name} {shape.data.area} reduce expected")
        expected_area -= shape.data.area
      else:
        if self.VERBOSE: print(f"{layer.label} {shape.name} {shape.data.area}")
        total_area += shape.data.area
    return (total_area, expected_area)

  def prettyPrint(self):
    ''' text dump of a cell to screen
    '''
    print(f"{self.x=} {self.y=} {self.clen=}")
    for layer in self.bft:
      shape = layer.this
      meta  = f"{layer.label} {layer.facing:<6} {shape.name:<12} "
      meta += '' if shape.data is None else f"{shape.data.bounds}" 
      print(meta) 

'''
the
end
'''
