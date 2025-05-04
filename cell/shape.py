import math
from .geomink import Plotter
from .meander import Meander
from shapely.geometry import Point, LinearRing, Polygon
from shapely import transform
'''
from shapely.geometry import Polygon, MultiPolygon, LinearRing
Shape is the lowest level geometry
Cell is a collection of shapes organised by layer
'''

class Points:
  ''' nw n ne    do the maths to render a cell
      w  c  e    points are calculated and called as p.ne p.s
      sw s se    
                 a collection of Shapely Points
                 for Triangles and Diamonds
  '''
  def __init__(self, x, y, stroke_width, clen):
    sw       = stroke_width
    cl       = clen
    self.n   = Point([x + cl / 2, y + sw])
    self.e   = Point([x + cl - sw, y + cl / 2])
    self.s   = Point([x + cl / 2, y + cl - sw])
    self.w   = Point([x + sw, y + cl / 2])
    self.ne  = Point([x + cl - sw, y + sw] )
    self.se  = Point([x + cl - sw, y + cl - sw])
    self.nw  = Point([x + sw, y + sw])
    self.sw  = Point([x + sw, y + cl - sw])
    self.mid = Point([x + cl / 2, y + cl / 2])

class Shape:
  ''' Shape needs exactly one inner class defined during init
  '''
  class Triangl(Points):
    ''' a linear ring wrapped in a Polygon 
        the wrapper is needed by transform
    '''
    def __init__(self):
      self.name = 'triangl'

    def draw(self, x, y, clen, swidth=0, facing=str(), size='medium'):
      super().__init__(x, y, swidth, clen)
      rings = {
        'north': LinearRing((self.nw, self.ne, self.s)),
        'south': LinearRing((self.sw, self.n, self.se)),
         'east': LinearRing((self.nw, self.e, self.sw)),
         'west': LinearRing((self.w, self.ne, self.se))
      }
      if facing in rings:
        self.data = Polygon(rings[facing])
      else:
        raise IndexError(f"Cannot face triangle {facing}")

    def svg(self, meander=False, facing=None):
      ''' return Meander, fallback or fill
      '''
      if meander or facing:
        raise NotImplementedError()
      p = [f"{c[0]},{c[1]}" for c in list(self.data.boundary.coords)]
      return { 'points': ','.join(map(str, list(p))) }

    def plotData(self): return self.data.boundary, self.name

  class Diamond(Points):
    def __init__(self):
      self.name = 'diamond'

    def draw(self, x, y, clen, swidth=0, facing=str(), size='medium'):
      super().__init__(x, y, swidth, clen)
      rings = {
        'all': LinearRing((self.w, self.n, self.e, self.s)),
       'west': LinearRing((self.w, self.n, self.s)),
       'east': LinearRing((self.n, self.e, self.s)),
      'north': LinearRing((self.w, self.n, self.e)),
      'south': LinearRing((self.w, self.e, self.s))
      }
      if facing in rings:
        self.data = Polygon(rings[facing])
      else:
        raise IndexError(f"Cannot face diamond {facing}")

    # TODO make this re-usable for any SVG polygon
    def svg(self, meander=False, facing=None):
      if meander or facing: raise NotImplementedError
      p = [f"{c[0]},{c[1]}" for c in list(self.data.boundary.coords)]
      return { 'points': ','.join(map(str, p)) }

    def plotData(self): return self.data.boundary, self.name

  class Circle(Points):
    def __init__(self):
      self.name = 'circle'

    def draw(self, x, y, clen, swidth=0, facing='all', size=str()):
      ''' pythagoras was a pythonista :)
      '''
      super().__init__(x, y, swidth, clen)
      large = clen / 2
      sum_two_sides = (large**2 + large**2)
      sizes = {
         'large': (math.sqrt(sum_two_sides) - swidth),
        'medium': (clen / 2 - swidth),
         'small': (clen / 3 - swidth)
      }
      if size in sizes:
        radius    = sizes[size]
        self.data = Point(self.mid.x, self.mid.y).buffer(radius)
      else:
        raise IndexError(f"Cannot set circle to {size} size")

    def svg(self, meander=False, facing=None):
      if meander or facing: raise NotImplementedError
      x, y, w, h = self.data.bounds
      r = round(self.data.centroid.x - x)
      return { 'cx': round(x), 'cy': round(y), 'r': r }

    def plotData(self):
      return self.data.boundary, self.name

  class Rectangle():
    ''' squares and lines
    '''
    VERBOSE = True

    def __init__(self, name):
      self.name = name

    def draw(self, x, y, clen, swidth=0, size=str(), facing=str()):
      ''' generate a shapely polygon
      '''
      sizes = dict()
      sw  = swidth
      hsw = swidth / 2 # TODO scale half stroke width
      cs  = clen  
      t3  = cs / 3    # three times smaller
      ''' input can be any of the four cardinal directions
          but only two are used so we silently collapse the others
      '''
      facing = 'north' if facing == 'south' else facing
      facing = 'east' if facing == 'west' else facing

      if self.name == 'square':  
        sizes = {
          'medium': [(x + hsw), 
                     (y + hsw), 
                     (cs - sw), 
                     (cs - sw)],
          'large':  [(x - t3 / 2 + hsw), 
                     (y - t3 / 2 + hsw),
                     (cs + t3 - sw), 
                     (cs + t3 - sw)],
          'small':  [(x + t3 + hsw), 
                     (y + t3 + hsw), 
                     (t3 - sw),
                     (t3 - sw)]
        }
      elif self.name == 'line' and facing == 'north':
        sizes = {
          'large': [(x + cs / 3 + hsw), 
                    (y - cs / 3 + hsw),
                    (cs / 3 - sw), 
                    ((cs / 3 * 2 + cs) - sw)],
          'medium': [(x + cs / 3 + hsw), 
                     (y + hsw), 
                     cs / 3 - sw, 
                     (cs - sw)],
          'small': [(x + cs / 3 + hsw), 
                    (y + cs / 4 + hsw),
                    (cs / 3 - sw),
                    (cs / 2 - sw)]
        }
      elif self.name == 'line' and facing == 'east':
        sizes = {
          'large': [(x - cs / 3 + hsw),
                    (y + cs / 3 + hsw),
                    ((cs / 3 * 2 + cs) - sw),
                    (cs / 3 - sw)],
          'medium': [(x + hsw),
                     (y + cs / 3 + hsw),
                     (cs - sw),
                     (cs / 3 - sw)],
          'small': [(x + cs / 4 + hsw),
                    (y + cs / 3 + hsw),
                    (cs / 2 - sw),
                    (cs / 3 - sw)]
        }
      if size in sizes:
        x, y, w, h = sizes[size]
        self.data  = Polygon([
          (x, y), (x, y + h), (x + w, y + h), (x + w, y)
        ]) # 4 corners
        #print(f"{self.name=} {size=} {x} {y} {w} {h}")
        #print(list(self.data.boundary.coords))
      else:
        raise IndexError(f"Cannot make {self.name} with {size}")

    def compute(self, polygon): 
      ''' experimental!
          idea is .draw() is the interface for user-generated cell
          .compute() is for machine-generated i.e. Shapely diff
      '''
      self.data = polygon

    def plotData(self):
      return self.data.boundary, self.name

    def svg(self, meander=False, facing=None):
      ''' markup a square
      '''
      if meander and facing:
        return self.lineFill(facing)
      elif meander:   # TODO duplicate code, see parabola
        x = [x for x in list(self.data.boundary.xy)[0]]
        y = [y for y in list(self.data.boundary.xy)[1]]
        p = [f"{x[i]},{y[i]}" for i in range(len(x))]
        points = ' '.join(map(str, p))
        return { 'points': points, 'name': self.name }
      else:
        coords = list(self.data.boundary.coords)
        x      = coords[0][0]
        y      = coords[0][1]
        width  = coords[2][0] - x
        height = coords[2][1] - y
        #print(x, y, width, height)
        return { 'x': x, 'y': y, 'width': width, 'height': height }

    def lineFill(self, facing, conf=dict(), label=None):
      '''
      self.label = label
      if facing is None and self.label in conf:
        direction = conf[self.label]
      elif direction:
        pass # por ejemplo E
      else:
        direction = 'N'
      '''
      d         = self.control(facing)
      m         = Meander(self.data)
      padme     = m.pad()
      guides    = m.guidelines(padme, d)
      points, e = m.collectPoints(padme, guides)
      if e and self.VERBOSE:
        raise ValueError(f"{e=} {self.label=} {facing=}")
      elif e:
        linefill = LineString()
      else:
        linefill = m.makeStripes(points)
      return linefill

    def control(self, direction):
      control = {
        'N': ('EB', 'ET'),
        'north': ('EB', 'ET'),
        'all': ('EB', 'ET'),
        'S': ('EB', 'ET'),
        'E': ('NL', 'NR'),
        'east': ('NL', 'NR'),
        'W': ('NL', 'NR')
      }
      if direction in control:
        return control[direction]
      else: # abandon if there are no guidelines defined
        raise KeyError(f'all at sea > {direction=} {self.label=} not found')

  class Void():
    ''' minimal class so flatten can handle danglers
    '''
    def __init__(self): self.name = 'void'

    def compute(self, polygon): self.data = polygon

    def lineFill(self, facing): return None # signal that no markup is required

  class Parabola:
    ''' u-shaped parallelograms
        north n south u ... 
    '''
    VERBOSE = False
    def __init__(self):
      self.name = 'parabola'
      #self.writer   = Plotter() TODO add plotData()

    def compute(self, polygon): self.data =  polygon

    def svg(self, meander=False, facing=None):
      ''' make u-shaped svg path 
      return boundary until meander from computed shape is ready
      '''
      if meander and facing:
        return self.lineFill(direction=facing)
      elif meander:
        x = [x for x in list(self.data.boundary.xy)[0]]
        y = [y for y in list(self.data.boundary.xy)[1]]
        p = [f"{x[i]},{y[i]}" for i in range(len(x))]
        points = ' '.join(map(str, p))
        return { 'points': points, 'name': self.name }
      else: raise NotImplementedError
        
    def lineFill(self, facing, conf=dict(), label=None):
      self.label = label  # TODO is label a-z or P1-n ??
      #direction  = direction if direction else conf[self.label]
      direction  = facing
      X, Y, W, H = self.data.bounds
      width      = W - X
      height     = H - Y
      clockwise  = self.setClock(width, height)
      surround   = Polygon([(X,Y), (X,H), (W,H), (W,Y)]) # four corners
      done       = surround.difference(self.data)
      x, y, w, h = done.bounds

      if direction == 'north':   # used to be N
        gnomon   = Polygon([(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)])
        rectangl = Polygon([(w,y),(w,h),(W,h),(W,Y)])
      elif direction == 'west': 
        gnomon   = Polygon([(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)])
        rectangl = Polygon([(x,Y),(x,y),(W,y),(W,Y)])
      elif direction == 'south':
        gnomon   = Polygon([(X,Y),(X,H),(x,h),(x,y),(W,y),(W,Y)])
        rectangl = Polygon([(w,y),(w,h),(W,H),(W,y)])
      elif direction == 'east':
        gnomon   = Polygon([(X,h),(X,H),(W,H),(W,Y),(w,Y),(w,h)])
        rectangl = Polygon([(X,Y),(X,y),(w,y),(w,Y)])
      else:
        raise NotImplementedError(f'all at sea > {direction} <')

      if gnomon.is_valid and rectangl.is_valid:
        g    = Meander(gnomon)
        gpad = g.pad()
        r    = Meander(rectangl)
        rpad = r.pad()
      elif not rectangl.is_valid and self.VERBOSE:
        raise ValueError(f"{rectangl.is_valid=} is not a good polygon")
        # { 'points': self.data.boundary } # fallback to outline
        '''
        p = [f"{c[0]},{c[1]}" for c in list(self.data.boundary.xy)]
        p = [f"{c[0]},{c[1]}" for c in list(self.data.boundary.xy)]
        return { 'points': ','.join(map(str, p)) }
        '''
      elif not gnomon.is_valid and self.VERBOSE:
        raise ValueError(f"{gnomon.is_valid=} {gnomon.boundary}")
  
      gcontrol = self.control('G', direction, clockwise)
      rcontrol = self.control('R', direction, clockwise)
      gmls     = g.guidelines(gpad, gcontrol)
      rmls     = r.guidelines(rpad, rcontrol)

      p1, e1  = g.collectPoints(gpad, gmls)
      p2, e2  = r.collectPoints(rpad, rmls)
      if e1 or e2:
        if self.VERBOSE: 
          print(f"{self.label} {e1=} {e2=} {direction}")
          print(f"""{self.label=} {clockwise=} {direction=} 
{gnomon=} 
{gmls=} 
{rectangl=} 
{rmls=} """)
          #self.writer.plot(gpad, rpad, fn=self.label)
        linefill = list(self.data.boundary.xy)
      else:
        linefill = r.joinStripes(p1, p2)
      return linefill
  
    def setClock(self, width, height):
      ''' meandering an odd number of stripes requires 
          direction order to be clockwise
          even stripes must be anti-clockwise
  
          tests suggest that when num of stripes is 1 then 
          clockwise should be True
          ignoring that corner case for now ..
      ''' 
      raw_stripes   = (width - 1) / 3         # padding reduces width
      numof_stripes = math.floor(raw_stripes) # round down
      clockwise     = False if numof_stripes % 2 else True
      return clockwise

    def control(self, shape, direction, clockwise):
      ''' get the right guideline
      '''
      control = {
        'G': { 
          'north': { True:  ('SR', 'SE', 'EB'), False: ('EB', 'SE', 'SR')}, 
          'south': { True:  ('NR', 'NE', 'ET'), False: ('ET', 'NE', 'NR')},
           'east': { True:  ('WB', 'SW', 'SL'), False: ('SL', 'SW', 'WB')},
           'west': { True:  ('EB', 'SE', 'SR'), False: ('SR', 'SE', 'EB')} 
        },
        'R': {
          'north': { True: ('NL', 'NR'), False: ('EB', 'ET')},
          'south': { True: ('EB', 'ET'), False: ('ET', 'EB')},
           'east': { True: ('SR', 'SL'), False: ('SL', 'SR')},
           'west': { True: ('WT', 'WB'), False: ('WT', 'WB')}
        }
      }
      if (shape in control 
        and direction in control[shape] 
        and clockwise in control[shape][direction]):
        return control[shape][direction][clockwise]
      else:
        raise KeyError(f'''
all at sea > {shape} {direction} {clockwise} < without control''')

  class SquareRing:
    ''' Shapely Polygon with a hole innit
    '''
    VERBOSE = False

    def __init__(self):
      self.name = 'sqring'

    ''' for machine generated shapes
    '''
    def compute(self, polygon): 
      if len(polygon.interiors) == 1:
        self.data = polygon
      else: raise TypeError(f"{len(polygon.interiors)=} not a sqring")

    def svg(self):
      '''
      p = [f"{x[i]},{y[i]}" for i in range(len(x))]
      points = ' '.join(map(str, p))
      '''

    def lineFill(self, facing, conf=dict(), label=None):
      ''' square ring is not currently accepting config
      ''' 
      self.label = label
      X, Y, W, H = self.data.bounds
      surround   = Polygon([(X,Y), (X,H), (W,H), (W,Y)]) # four corners
      done       = surround.difference(self.data)
      x, y, w, h = done.bounds
      nw         = Polygon([(X,Y), (X,H), (W,H), (W,h), (x,h), (x,Y)])
      se         = Polygon([(x,Y), (x,y), (w,y), (w,h), (W,h), (W,Y)])

      if nw.is_valid and se.is_valid:
        m1  = Meander(nw)
        m2  = Meander(se)
        nwp = m1.pad()
        sep = m2.pad()
      else:
        if self.VERBOSE: 
          print(f"{self.label} is not a good polygon")
          self.writer.plot(surround, self.parabola, fn=self.label)
        return LineString()

      nw_mls = m1.guidelines(nwp, ('WB', 'NW', 'NR'))
      se_mls = m2.guidelines(sep, ('SL', 'SE', 'ET'))
      p1, e1 = m1.collectPoints(nwp, nw_mls)
      p2, e2 = m2.collectPoints(sep, se_mls)
      if e1 or e2:  # silently fail
        combined = list(nwp.exterior.coords) + list(sep.exterior.coords)
        linefill = LinearRing(combined)
        '''
        inner  = list(self.sqring.interiors)
        coords = outer
        [inner_p.append(list(lring.coords)) for lring in inner]
        '''
        if e1 and self.VERBOSE:
          print(f"{self.label} {e1}")
        elif e2 and self.VERBOSE:
          print(f"{self.label} {e2}")
      else:
        linefill = m1.joinStripes(p1, p2)
      return linefill
  
  def __init__(self, label, celldata=dict()):
    ''' create a Shapely shape to put in a layered Cell
    '''
    name = celldata['shape'] if 'shape' in celldata else 'square' 
    shapes = { 
      'circle': self.Circle(), 
      'diamond': self.Diamond(),
      'triangl': self.Triangl(), 
      'line': self.Rectangle(name), 
      'square': self.Rectangle(name),
      'void': self.Void(),
      'parabola': self.Parabola(),
      'sqring': self.SquareRing()
    }
    self.this  = shapes[name]
    self.label = label
    self.setCell(celldata)

  def setCell(self, c):
    ''' encapsulate cell data from db or define some default values
    '''
    self.size   = c['size']   if 'size'   in c else 'medium'
    self.facing = c['facing'] if 'facing' in c else 'north'
    self.fill   = c['fill']   if 'fill'   in c else 'FFF'
    # remove hash for consistency
    if list(self.fill)[0] == '#': self.fill = self.fill[1:] 
    if 'fill_opacity' in c:
      self.opacity = c['fill_opacity']
    else:
      self.opacity = 1
    if 'stroke' in c:
      self.stroke  = {
        'fill':      c['stroke'],
        'dasharray': c['stroke_dasharray'],
        'opacity':   c['stroke_opacity'],
        'width':     c['stroke_width']
      }
    else:
      self.stroke = None

  def plot(self):
    p = Plotter()
    data, name = self.this.plotData()
    p.plotLine(data, name)

  def compute(self, data):
    ''' facing is supposed to be inherited
    but as we already know where square rings face
    it is hard coded here
    '''
    if self.facing:
      self.this.compute(data)
    elif self.this.name == 'sqring':  # TODO see direct() sqring have no face
      self.facing = 'all'
      self.this.compute(data)
    else:
      raise ValueError('faceless cannot compute')

  def draw(self, x, y, clen):
    ''' wrapper to this.draw
    '''
    stroke_width = 0 if not self.stroke else self.stroke['width']
    self.this.draw(
      x, y, clen, swidth=stroke_width, facing=self.facing, size=self.size
    )

  def tx(self, x, y):
    ''' use Shapely transform to offset coordinates 
        according to grid position
    if line_string.geom_type == 'LineString':
    '''
    if self.this.data.geom_type == 'Polygon':
      if len(self.this.data.interiors) == 0:
        boundary       = self.this.data.boundary 
        line_string    = transform(boundary, lambda a: a + [x, y])
        self.this.data = Polygon(line_string)
        # print(f"{x} {y} {self.label} {line_string}")
      elif len(self.this.data.interiors) == 1: # deal with sqring
        lse = transform(self.this.data.exterior, lambda a: a + [x, y])
        lsi = transform(self.this.data.interiors[0], lambda a: a + [x, y])
        # print(f"{x} {y} {self.label} {list(lsi.coords)}")
        self.this.data = Polygon(lse, holes=[list(lsi.coords)])
      else:
        raise NotImplementedError
    else: raise TypeError(f"""
{self.this.data.geom_type} unexpected: '{self.label}' {self.this.name}""")

  def svg(self, meander=False):
    ''' expose shape SVG methods 
        return Shapely as markup in three formats
        1. polyline with Meander 
        2. polyline from Shapely.boundary
        3. polygon
    '''
    if meander and self.facing:
      linefill = self.this.lineFill(facing=self.facing)
      if linefill:  # void returns None
        p = [f"{c[0]},{c[1]}" for c in list(linefill.coords)]
        return { 'points': ','.join(map(str, p)), 'name': self.this.name }
      else:
        return { 'points': 'none', 'name': self.this.name }
    else:
      svg = self.this.svg()
      if 'name' in svg: print(f"{self.this.name} double handled")
      svg['name'] = self.this.name
      return svg
'''
the
end
'''
