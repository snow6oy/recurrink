from shapely.geometry import Polygon, LineString
from .shape import *

class Layer:

  VERBOSE = False

  def __init__(self, pos=tuple([0,0]), clen=60): 
    self.bft       = list()
    self.direction = list()   # make guide for meander
    self.clen      = clen     # length of cell
    self.pos       = pos      # logical position in block

  def background(self): 
    x = self.pos[0] * self.clen
    y = self.pos[1] * self.clen
    w = x + self.clen # a square has same width and height 
    h = y + self.clen
    self.bft.append(((x, y), (x, h), (w, h), (w, y)))
    # self.direction.append('all') TODO map all to spiral
    self.direction.append(('EB','ET'))

  def foreground(self, **kwargs):
    ''' Block.walk also calls here when top
    '''
    name   = kwargs['shape'] if 'shape' in kwargs else 'square'
    shapes = {
      'line': Rectangle(name),
      'square': Rectangle(name),
      'gnomon': Gnomon()
    }
    shape     = shapes[name]
    coords    = shape.coords(self.pos[0], self.pos[1], self.clen, kwargs)
    if len(coords): self.bft.append(coords)
    self.direction.append(shape.guide(kwargs['facing']))

  def polygon(self):
    if len(self.bft) == 3:
      p = Polygon(self.bft[0], holes=[self.bft[1], self.bft[2]])
    else:             # must be two right ?
      p = Polygon(self.bft[0], holes=[self.bft[1]])
    return p
'''
the
end
'''
