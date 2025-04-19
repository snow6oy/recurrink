from .shape import Shape

class CellMaker:

  VERBOSE = False
 
  def __init__(self, pos, clen):
    self.x    = int(pos[0] * clen)
    self.y    = int(pos[1] * clen)
    self.clen = clen
    self.bft  = list() # b0 background f1 foreground t2 top

  def background(self, label, cell):
    ''' basic square with colour
    '''
    bg_cell = { 'shape': 'square', 'fill': cell['bg'], 'fill_opacity': 1 }
    bg      = Shape(label, bg_cell)
    bg.this.draw(self.x, self.y, 0, self.clen, size='medium', facing='all')
    self.bft.append(bg)

  def foreground(self, label, cell=dict()):
    fg = Shape(label, cell)
    sw = fg.stroke['width'] if fg.stroke else 0
    fg.this.draw(self.x, self.y, sw, self.clen, 
      size=fg.size, facing=fg.facing
    )
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
    void.this.draw(shape)
    self.bft.append(void)

  def getStyle(self, i): # layer index
    ''' construct a CSS style 
    '''
    if i == 0: # force stroke width zero to hide cracks between backgrounds
      style = f"fill:#{self.bft[0].fill};stroke-width:0" 
    else:
      style = (f"fill:#{self.bft[i].fill};" +
        f"fill-opacity:{self.bft[i].opacity}")
      if self.bft[i].stroke['width']:
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
    if self.VERBOSE: print(f"{len(self.bft)=}")
    if len(self.bft) == 4:
      self.bft[2] = self.evalSeeker(self.bft[3], self.bft[2])
      self.bft[1] = self.evalSeeker(self.bft[3], self.bft[1])
      self.bft[0] = self.evalSeeker(self.bft[3], self.bft[0])
    elif len(self.bft) == 3:
      self.bft[1] = self.evalSeeker(self.bft[2], self.bft[1])
      self.bft[0] = self.evalSeeker(self.bft[2], self.bft[0])
    self.bft[0] = self.evalSeeker(self.bft[1], self.bft[0])

  def evalSeeker(self, done, seek):
    ''' done are immutable and already cell members
        seekers may be included, depends on what overlaps with done
        return seeker either modified, emptied or as-is
    ''' 
    if self.VERBOSE: print(f"{len(self.bft)=} {len(done)=} {len(seek)=}")
    if done.this.data.equals(seek.this.data): # fg completely covers bg
      seek.this.data = None
      seek.this.name = 'invisible'
    else:
      diff = seek.this.data.difference(done.this.data)
      if self.VERBOSE: print(f"{done.label=} {seek.this.name=} {diff.bounds}")
      if diff.is_empty:   # nothing overlapped
        pass              # return seek as it came
      else:
        if diff.geom_type == 'MultiPolygon':
          seek.this.name = 'multipolygon'
        else:
          seek.this.name = self.identify(diff)
        seek.this.data = diff
    return seek

  def identify(self, shape):
    ''' attempt to identify a shape that Meander.fill can handle 
        default to Irregular if none 
    '''
    if shape.geom_type == 'MultiPolygon':
      raise NotImplementedError(f'cannot identify {shape.geom_type}')

    if self.shapeTeller(shape, 'rectangle'):
      label = 'square'
    elif self.shapeTeller(shape, 'gnomon'):
      label = 'G'
    elif self.shapeTeller(shape, 'parabola'):
      label = 'parabola'  # aka P
    elif self.shapeTeller(shape, 'sqring'):
      label   = 'sqring'
    else:  # raise TypeError(f'unidentified {shape.geom_type}')
      label = 'I'   
    #return self.stickLabel(label)
    return label

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
'''
the
end
'''
