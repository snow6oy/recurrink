import math
from .geomink import Plotter
from shapely.geometry import Point, LinearRing, Polygon

'''
rename Geomink to Layer
x consider layer[0].points() as conversion from Shape
convert Points to Shapely
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
    def __init__(self):
      self.name = 'triangl'

    def draw(self, x, y, stroke_width, clen, facing=str()):
      super().__init__(x, y, stroke_width, clen)
      rings = {
        'north': LinearRing((self.nw, self.ne, self.s)),
        'south': LinearRing((self.sw, self.n, self.se)),
         'east': LinearRing((self.nw, self.e, self.sw)),
         'west': LinearRing((self.w, self.ne, self.se))
      }
      if facing in rings:
        self.data = rings[facing]
      else:
        raise IndexError(f"Cannot face triangle {facing}")

    def svg(self):
      p = [f"{c[0]},{c[1]}" for c in list(self.data.coords)]
      return ','.join(map(str, list(p)))

    def plotData(self):
      return self.data, self.name

  class Diamond(Points):
    def __init__(self):
      self.name = 'diamond'

    def draw(self, x, y, stroke_width, clen, facing=str()):
      super().__init__(x, y, stroke_width, clen)
      rings = {
        'all': LinearRing((self.w, self.n, self.e, self.s)),
       'west': LinearRing((self.w, self.n, self.s)),
       'east': LinearRing((self.n, self.e, self.s)),
      'north': LinearRing((self.w, self.n, self.e)),
      'south': LinearRing((self.w, self.e, self.s))
      }
      if facing in rings:
        self.data = rings[facing]
      else:
        raise IndexError(f"Cannot face diamond {facing}")

    def svg(self):
      p = [f"{c[0]},{c[1]}" for c in list(self.data.coords)]
      return { 'points': ','.join(map(str, p)) }

    def plotData(self):
      return self.data, self.name

  class Circle(Points):
    def __init__(self):
      self.name = 'circle'

    def draw(self, x, y, stroke_width, clen, size=str()):
      ''' pythagoras was a pythonista :)
      '''
      super().__init__(x, y, stroke_width, clen)
      large = clen / 2
      sum_two_sides = (large**2 + large**2)
      sizes = {
         'large': (math.sqrt(sum_two_sides) - stroke_width),
        'medium': (clen / 2 - stroke_width),
         'small': (clen / 3 - stroke_width)
      }
      if size in sizes:
        radius    = sizes[size]
        self.data = Point(self.mid.x, self.mid.y).buffer(radius)
      else:
        raise IndexError(f"Cannot set circle to {size} size")

    def svg(self):
      x, y, w, h = self.data.bounds
      r = round(self.data.centroid.x - x)
      return { 'cx': round(x), 'cy': round(y), 'r': r }

    def plotData(self):
      return self.data.boundary, self.name

  class Rectangle():
    def __init__(self, name):
      self.name = name

    def draw(self, x, y, width, clen, size=str(), facing=str()):
      ''' generate a shapely polygon
      '''
      sizes = dict()
      sw  = width
      hsw = width / 2 # TODO scale half stroke width
      cs  = clen  
      t3  = cs / 3    # three times bigger
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
        self.data  = Polygon([(x,y), (x,h), (w,h), (w,y)]) # four corners
      else:
        raise IndexError(f"Cannot make {self.name} with {size}")

    def plotData(self):
      return self.data.boundary, self.name

    def svg(self):
      ''' markup a square
      '''
      x, y, width, height = self.data.bounds
      return { 'x': x, 'y': y, 'width': width, 'height': height }
  
  def __init__(self, n=str()):
    ''' scale is no longer applied to shapes
    '''
    shapes = { 
      'circle': self.Circle(), 
      'diamond': self.Diamond(),
      'triangl': self.Triangl(), 
      'line': self.Rectangle(n), 
      'square': self.Rectangle(n) 
    }
    self.shape = shapes[n]

  def plot(self):
    p = Plotter()
    data, name = self.shape.plotData()
    p.plotLine(data, name)

class ShapelyCell:
  def __init__(self, name, pos, clen):
    self.name = name
    self.pos  = pos
    self.clen = clen
    self.bft  = list() # b0 background f1 foreground t2 top

  def background(self):
    ''' TODO add colour
    '''
    x, y = self.pos
    bg   = Shape('square')
    bg.shape.draw(x, y, 0, self.clen, size='medium', facing='all')
    self.bft.append(bg)

  def foreground(self, cell):
    x, y = self.pos
    fg   = Shape(cell['shape'])
    fg.shape.draw(
      x, y, cell['stroke_width'], self.clen, 
      size=cell['size'], facing=cell['facing']
    )
    self.bft.append(fg)
'''
the
end
'''
