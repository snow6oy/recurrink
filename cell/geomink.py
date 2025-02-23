import math
import pprint
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
from shapely import transform
from .meander import Meander
from .shapes import Shapes
pp = pprint.PrettyPrinter(indent=2)

class Geomink(Shapes):
  ''' recurrink wrapper around Shapely geometries
  '''
  class Rectangle:
    VERBOSE = False

    def __init__(self, rectangl): #, label=None):
      self.rectangl = rectangl
      #self.label    = label

    def fill(self, direction=None, conf=dict(), label=None):
      self.label = label
      if direction is None and self.label in conf:
        direction = conf[self.label]
      else:
        direction = 'N'
      d         = self.control(direction)
      m         = Meander(self.rectangl)
      padme     = m.pad()
      guides    = m.guidelines(padme, d)
      points, e = m.collectPoints(padme, guides)
      if e and self.VERBOSE:
        raise ValueError(err + self.label, direction)
      elif e:
        linefill = LineString()
      else:
        linefill = m.makeStripes(points)
      return linefill

    def control(self, direction):
      control = {
        'N': ('EB', 'ET'),
        'S': ('EB', 'ET'),
        'E': ('NL', 'NR'),
        'W': ('NL', 'NR')
      }
      if direction in control:
        return control[direction]
      else: # abandon if there are no guidelines defined
        raise KeyError(f'all at sea > {direction=} {self.label=} not found')

  class Parabola:
    ''' u-shaped parallelograms
        north n south u ... 
    '''
    VERBOSE = False

    def __init__(self, parabola, label):
      self.parabola = parabola
      self.label    = label
      self.writer   = Plotter()

    def fill(self, direction=None, conf=dict(), label=None):
      self.label = label
      direction  = direction if direction else conf[self.label]
      X, Y, W, H = self.parabola.bounds
      width      = W - X
      height     = H - Y
      clockwise  = self.setClock(width, height)
      surround   = Polygon([(X,Y), (X,H), (W,H), (W,Y)]) # four corners
      done       = surround.difference(self.parabola)
      x, y, w, h = done.bounds

      if direction == 'N':
        gnomon   = Polygon([(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)])
        rectangl = Polygon([(w,y),(w,h),(W,h),(W,Y)])
      elif direction == 'W': 
        gnomon   = Polygon([(X,Y),(X,H),(W,H),(W,h),(x,h),(x,Y)])
        rectangl = Polygon([(x,Y),(x,y),(W,y),(W,Y)])
      elif direction == 'S':
        gnomon   = Polygon([(X,Y),(X,H),(x,h),(x,y),(W,y),(W,Y)])
        rectangl = Polygon([(w,y),(w,h),(W,H),(W,y)])
      elif direction == 'E':
        gnomon   = Polygon([(X,h),(X,H),(W,H),(W,Y),(w,Y),(w,h)])
        rectangl = Polygon([(X,Y),(X,y),(w,y),(w,Y)])
      else:
        raise NotImplementedError(f'all at sea > {direction} <')

      if gnomon.is_valid and rectangl.is_valid:
        g    = Meander(gnomon)
        gpad = g.pad()
        r    = Meander(rectangl)
        rpad = r.pad()
      else:
        print(f"{self.label} is not a good polygon")
        if self.VERBOSE: self.writer.plot(surround, self.parabola, fn=self.label)
        return self.parabola.boundary
  
      gcontrol = self.control('G', direction, clockwise)
      rcontrol = self.control('R', direction, clockwise)
      gmls     = g.guidelines(gpad, gcontrol)
      rmls     = r.guidelines(rpad, rcontrol)

      #print(f""" {self.label=} {clockwise=} {direction=} {gnomon=} {gmls=} {rectangl=} {rmls=} """)
      p1, e1  = g.collectPoints(gpad, gmls)
      p2, e2  = r.collectPoints(rpad, rmls)
      if e1 or e2:
        print(f"{self.label} {e1=} {e2=} {direction}")
        if self.VERBOSE: self.writer.plot(gpad, rpad, fn=self.label)
        linefill = LineString()
      else:
        linefill = r.joinStripes(p1, p2)
      return linefill
  
    def setClock(self, width, height):
      ''' meandering an odd number of stripes requires direction order to be clockwise
          even stripes must be anti-clockwise
  
          tests suggest that when num of stripes is 1 then clockwise should be True
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
        'G': { 'N': { True:  ('SR', 'SE', 'EB'),    # t.parabola.Test.test_12
                      False: ('EB', 'SE', 'SR')},   # t.parabola.Test.test_7
               'S': { True:  ('NR', 'NE', 'ET'),    # t.parabola.Test.test_5
                      False: ('ET', 'NE', 'NR')},   # t.parabola.Test.test_6
               'E': { True:  ('WB', 'SW', 'SL'),    # t.parabola.Test.test_9
                      False: ('SL', 'SW', 'WB')},   # t.parabola.Test.test_8
               'W': { True:  ('EB', 'SE', 'SR'),    # t.parabola.Test.test_11
                      False: ('SR', 'SE', 'EB')}    # t.parabola.Test.test_10
        },
        'R': { 'N': { True:  ('NL', 'NR'),
                      False: ('EB', 'ET')},
               'S': { True:  ('EB', 'ET'),
                      False: ('ET', 'EB')},
               'E': { True:  ('SR', 'SL'),
                      False: ('SL', 'SR')},
               'W': { True:  ('WT', 'WB'),
                      False: ('WT', 'WB')}
        }
      }
      if shape in control and direction in control[shape] and clockwise in control[shape][direction]:
        return control[shape][direction][clockwise]
      else:
        raise KeyError(f'all at sea > {shape} {direction} {clockwise} < without control')

  class Gnomon:
    ''' Gnomon has an area of IDGP that equals HPFB
    D  G  C
    I  P  F
    A  H  B
    https://en.wikipedia.org/wiki/Theorem_of_the_gnomon

    two out of four possible gnomon can be drawn here
        NW  +---  SE     |
            |         ---+
    '''
    VERBOSE = False

    def __init__(self, gnomon, label=None):
      self.gnomon = gnomon
      if label: self.label  = label
      self.writer   = Plotter()

    def fill(self, direction=None, conf=dict(), label=None):
      self.label = label
      direction = direction if direction else conf[self.label]
      d         = self.control(direction)
      m         = Meander(self.gnomon)
      padme     = m.pad()
      guides    = m.guidelines(padme, d)
      points, e = m.collectPoints(padme, guides)
      if e and self.VERBOSE:
        raise ValueError(err + self.label, direction)
        self.writer.plot(self.gnomon, padme, fn=self.label)
      elif e:
        linefill = LineString()
      else:
        linefill = m.makeStripes(points)
      return linefill

    def control(self, direction):
      control = {
        'N':  ('EB','ET'),    # experimental, tidy ?
        'E':  ('NL','NR'),
        'NW': ('WB', 'NW', 'NR'),
        'SE': ('SL', 'SE', 'ET')
      }
      if direction in control:
        return control[direction]
      else:
        raise KeyError(f'all at sea > {direction} <')

  class SquareRing:
    ''' Shapely Polygon with a hole innit
    '''
    VERBOSE = False

    def __init__(self, sqring, label):
      self.sqring = sqring
      self.label  = label

    def fill(self, conf=dict(), label=None):
      ''' square ring is not currently accepting config
      ''' 
      self.label = label
      X, Y, W, H = self.sqring.bounds
      surround   = Polygon([(X,Y), (X,H), (W,H), (W,Y)]) # four corners
      done       = surround.difference(self.sqring)
      x, y, w, h = done.bounds
      nw         = Polygon([(X,Y), (X,H), (W,H), (W,h), (x,h), (x,Y)])
      se         = Polygon([(x,Y), (x,y), (w,y), (w,h), (W,h), (W,Y)])

      if nw.is_valid and se.is_valid:
        m1  = Meander(nw)
        m2  = Meander(se)
        nwp = m1.pad()
        sep = m2.pad()
      else:
        print(f"{self.label} is not a good polygon")
        if self.VERBOSE: self.writer.plot(surround, self.parabola, fn=self.label)
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

  class Irregular:
    ''' Ideally Flatten would only produce Regular shapes
        but it does not and then Meander fails badly 
    '''
    def __init__(self, irregular, label):
      self.irregular = irregular
      self.label     = label
 
    def fill(self, conf=None, label=None):
      ''' an empty LineString will leave a hole
      '''
      return LineString()

  def __init__(self, cellsize, scale=1.0, pencolor='000', **kwargs):
    ''' a tuple with min and max coord will become a rectangle
        more complex shapes should be pre-generated and sent as a Geometry
        something of type: shapely.geometry.polygon.Polygon
        OR with x,y coords and celldata generate a rectangle using Shapes
        then generate polygon once xywh is known
        label is mandatory when Geomink is made from polygon

    print(f"{scale=} {pencolor=} {kwargs=}")
    print(f"{kwargs['xywh']=}, {kwargs['polygon']=}")
    '''
    super().__init__(scale, cellsize)
    # switching between fg and bg fills should happen before
    self.pencolor = pencolor 
    if 'xywh' in kwargs:
      xywh = kwargs['xywh']
    elif 'coord' in kwargs and 'cell' in kwargs and 'layer'in kwargs: 
      x, y = self.setCell(cellsize, kwargs)
      self.pencolor = self.fill
      if self.layer == 'bg': # override cell
        fg = self.foreground(x, y, { 
          'facing': 'all', 'shape': 'square', 'size': 'medium', 'stroke_width': 0 
        })
      else:
        fg = self.foreground(x, y, kwargs['cell']) # TODO obtain Cell vals from self instead
      x, y, w, h = list(fg.values())[:4]  # drop the name val cos we already know its square
      w += x
      h += y
      xywh = (x, y, w, h)
    else:
      xywh = tuple()

    if len(xywh) == 4: # defined by cells
      x, y, w, h  = xywh
      self.shape  = Polygon([(x,y), (x,h), (w,h), (w,y)]) # four corners
      self.meander = self.Rectangle(self.shape)
      self.label   = 'R'
    elif 'polygon' in kwargs and 'label' in kwargs:
      label = list(kwargs['label'])[0] # first char of string
      polygon = kwargs['polygon'] # of type: shapely.geometry.polygon.Polygon
      if label == 'R':  # rectangle
        self.meander = self.Rectangle(polygon)
      elif label == 'G': # gnomon
        self.meander = self.Gnomon(polygon, label)
      elif label == 'P': # parabola
        self.meander = self.Parabola(polygon, label)
      elif label == 'S': # sqring
       self.meander = self.SquareRing(polygon, label)
      elif label == 'I': # irregular
       self.meander = self.Irregular(polygon, label)
      else:
        raise ValueError(f'{label} unknown shape')
      self.shape  = Polygon(polygon)
      self.label  = label
    else:
      raise ValueError(f"{len(xywh)=} needs 4 OR polygon with label OR coord with cell and layer")

  def setCell(self, cellsize, cell):
    ''' encapsulate cell data from db
    '''
    if cell['cell']['shape'] not in ['square', 'line']:
      print(f"this {cell['shape']} is going to be interesting")

    c            = cell['cell']
    coord        = cell['coord']
    x            = int(coord[0] * cellsize)
    y            = int(coord[1] * cellsize)
    self.layer   = cell['layer']
    self.fill    = c['bg'] if self.layer == 'bg' else c['fill']
    self.opacity = c['fill_opacity']
    self.stroke  = {
      'fill':      c['stroke'],
      'dasharray': c['stroke_dasharray'],
      'opacity':   c['stroke_opacity'],
      'width':     c['stroke_width']
    }
    if list(self.fill)[0] == '#': self.fill = self.fill[1:] # remove # for consistency
    return x, y

  def tx(self, x, y):
    ''' use Shapely transform to offset coordinates according to grid position
    '''
    boundary    = self.shape.boundary
    line_string = transform(boundary, lambda a: a + [x, y])
    self.shape  = Polygon(line_string)

class Cell():
  '''
  a Cell is comprised of up to three layers
  each layer is a Geomink wrapper around a Shapely geometry object
  '''
  def __init__(self, name, cellsize, coord, cell):
   self.bft      = list()
   self.names    = list()
   self.cellsize = cellsize
   self.coord    = coord
   self.bft.append(Geomink(cellsize, coord=coord, cell=cell, layer='bg'))
   self.bft.append(Geomink(cellsize, coord=coord, cell=cell, layer='fg'))
   [self.names.append(name) for i in range(2)]

  def addTop(self, name, cell):
    if cell['top']:
      gmk = Geomink(self.cellsize, coord=self.coord, cell=cell, layer='top') 
      self.bft.append(gmk)
      self.names.append(name)

class Plotter:
  ''' wrapper around matplot so we can see whats going on
  '''
  def plot(self, p1, p2, fn):
    x1, y1 = p1.boundary.xy
    x2, y2 = p2.boundary.xy
    plt.plot(x1, y1, 'b-', x2, y2, 'r--')
    #plt.axis([0, 18, 0, 18])
    plt.savefig(f'tmp/{fn}.svg', format="svg")

  def plotLine(self, line, fn):
    if line.geom_type != 'LineString':
      raise ValueError(f'wrong geometry {line.geom_type}')
    fig, ax = plt.subplots()
    x = []
    y = []
    [x.append(c[0]) for c in list(line.coords)]
    [y.append(c[1]) for c in list(line.coords)]
    ax.plot(x, y)
    plt.savefig(f'tmp/{fn}.svg', format="svg")

  def multiPlot(self, mpn, fn):
    ''' multi polygon
      print(f"{g.geom_type=}")
      print(f"{list(g.exterior.coords)=}")
      print(f"{list(g.interiors)=}")
    '''
    colours = list('bgrcmyk')
    cindex  = 0
    for g in mpn.geoms:
      if len(list(g.interiors)):
        print(f"skipping {g.bounds}")
      else:
        x, y = g.boundary.xy
      format_str = str(f"{colours[cindex]}--")
      plt.plot(x, y, format_str)
      cindex += 1
    #plt.axis([0, 90, 0, 30])
    plt.savefig(f'tmp/{fn}.svg', format="svg")
    '''
    line.append([x, y, 'a']) #str(colours[cindex]])
    line = []
      x, y = geom.boundary.xy
    '''
'''
the
end
'''
