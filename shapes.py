import math
import pprint
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing 
from meander import Meander
pp = pprint.PrettyPrinter(indent=2)

class Geomink:
  ''' recurrink wrapper around Shapely geometries
  '''
  class Rectangle:
    VERBOSE = False

    def __init__(self, rectangl, label=None):
      self.rectangl         = rectangl
      if label: self.label  = label

    def fill(self, direction=None, conf=dict()):
      direction = direction if direction else conf[self.label]

      if direction in ['N', 'S']:
        d = ('EB','ET')
      elif direction in ['E', 'W']:
        d = ('NL','NR')
      else: # abandon if there are no guidelines defined
        raise NotImplementedError(f'all at sea > {direction=} {self.label=} not found')
      #print(direction, self.label, d)
      m        = Meander(self.rectangl)
      padme    = m.pad()
      guides   = m.guidelines(padme, d)
      points, err = m.collectPoints(padme, guides)
      if err and self.VERBOSE:
        raise ValueError(err + self.label, direction)
      elif err:
        linefill = LineString()
      else:
        linefill = m.makeStripes(points)
      return linefill

  class Parabola:
    ''' u-shaped parallelograms
        north n south u ... 
    '''
    VERBOSE = False

    def __init__(self, parabola, label):
      self.parabola = parabola
      self.label    = label
      self.writer   = Plotter()

    def fill(self, direction=None, conf=dict()):
      direction  = direction if direction else conf[self.label]

      X, Y, W, H = self.parabola.bounds
      width      = W - X
      height     = H - Y
      surround   = Polygon([(X,Y), (X,H), (W,H), (W,Y)]) # four corners

      if surround.is_valid:
        if width == height:
          indivisible_by_3 = bool(width % 3)
          if indivisible_by_3:
            print(f"""{self.label} indivisible by 3 {width=} {indivisible_by_3=} """)
            return LineString()
          else:
            done       = surround.difference(self.parabola)
            x, y, w, h = done.bounds
            clockwise  = self.setClock(width, height)
        else:
          print(f"""{self.label} not a square {width} {height} """)
          return LineString()
      else:
        print(f"""{self.label} in valid bounds {X} {Y} {W} {H} {x} {y} {w} {h} """)
        return LineString()

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
        return LineString()
  
      if direction == 'N' and clockwise:  # t.parabola.Test.test_12
        gmls = g.guidelines(gpad, ('SR', 'SE', 'EB'))
        rmls = r.guidelines(rpad, ('NL', 'NR'))
      elif direction == 'N':                   # t.parabola.Test.test_5
        gmls = g.guidelines(gpad, ('EB', 'SE', 'SR'))
        rmls = r.guidelines(rpad, ('EB', 'ET'))
      elif direction == 'S' and clockwise: # t.parabola.Test.test_7
        gmls = g.guidelines(gpad, ('NR', 'NE', 'ET'))
        rmls = r.guidelines(rpad, ('EB', 'ET'))
      elif direction == 'S':                    # t.parabola.Test.test_6
        gmls = g.guidelines(gpad, ('ET', 'NE', 'NR'))
        rmls = r.guidelines(rpad, ('ET', 'EB'))
      elif direction == 'E' and clockwise: # t.parabola.Test.test_9
        gmls = g.guidelines(gpad, ('WB', 'SW', 'SL'))
        rmls = r.guidelines(rpad, ('SR', 'SL'))
      elif direction == 'E':                    # t.parabola.Test.test_8
        gmls = g.guidelines(gpad, ('SL', 'SW', 'WB'))
        rmls = r.guidelines(rpad, ('SL', 'SR'))
      elif direction == 'W':                    # t.parabola.Test.test_11
        if clockwise:
          gmls = g.guidelines(gpad, ('EB', 'SE', 'SR'))
        else:                                        # t.parabola.Test.test_10
          gmls = g.guidelines(gpad, ('SR', 'SE', 'EB')) 
        rmls = r.guidelines(rpad, ('WT', 'WB'))
      else:
        raise NotImplementedError(f'all at sea > {direction} <')
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

    def zzsetClock(self, X, Y, W, H, ww, hh):
      ''' meandering an odd number of stripes requires direction order to be clockwise
          even stripes must be anti-clockwise
  
          tests suggest that when num of stripes is 1 then clockwise should be True
          ignoring that corner case for now ..
      ''' 
      width     = W - X
      height    = H - Y
      clockwise = None     # difference between False and None is .. err
      if width == height:
        if width % 3:
          raise Warning(f"expected seeker to be divisible by 3 {width=} {ww=} {hh=}")
        else:
          raw_stripes   = (width - 1) / 3         # padding reduces width
          numof_stripes = math.floor(raw_stripes) # round down
          clockwise     = False if numof_stripes % 2 else True
          #print(f"{round(numof_stripes)=} {clockwise=}")
      else:
        # non-square seekers will always fail ?
        raise Warning(f"{self.label} expected seeker to be square {width=} {height=}")
      return clockwise

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

    def fill(self, direction=None, conf=dict()):
      direction = direction if direction else conf[self.label]
      if direction == 'N':
        d = ('EB','ET')
      elif direction == 'NW':
        d = ('WB', 'NW', 'NR')
      elif direction == 'SE':
        d = ('SL', 'SE', 'ET')
      elif direction == 'E':
        d = ('NL','NR')
      else:
        raise NotImplementedError(f'all at sea > {direction} <')

      m           = Meander(self.gnomon)
      padme       = m.pad()
      guides      = m.guidelines(padme, d)
      points, err = m.collectPoints(padme, guides)
      if err and self.VERBOSE:
        raise ValueError(err + self.label, direction)
        self.writer.plot(self.gnomon, padme, fn=self.label)
      elif err:
        linefill = LineString()
      else:
        linefill = m.makeStripes(points)
      return linefill

  class SquareRing:
    ''' Shapely Polygon with a hole innit
    '''
    VERBOSE = False

    def __init__(self, sqring, label):
      self.sqring = sqring
      self.label  = label

    def fill(self, conf=dict()):
      ''' square ring is not currently accepting config
      '''
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

      nw_mls     = m1.guidelines(nwp, ('WB', 'NW', 'NR'))
      se_mls     = m2.guidelines(sep, ('SL', 'SE', 'ET'))
      p1, err    = m1.collectPoints(nwp, nw_mls)
      p2, err    = m2.collectPoints(sep, se_mls)
      if err and self.VERBOSE:
        raise ValueError(err + self.label)
      elif err:
        linefill = LineString()
      else:
        linefill = m1.joinStripes(p1, p2)
      return linefill

  def __init__(self, xywh=tuple(), polygon=None, pencolor='000', label=None):
    ''' a tuple with min and max coord will become a rectangle
        more complex shapes should be pre-generated and sent as a Geometry
        something of type: shapely.geometry.polygon.Polygon
    '''
    self.pencolor = pencolor
    # label is mandatory when Geomink is made from polygon
    if polygon and label: # type: shapely.geometry.polygon.Polygon
      if list(label)[0] == 'R':  # rectangle
        self.meander = self.Rectangle(polygon, label)
      elif list(label)[0] == 'G': # gnomon
        self.meander = self.Gnomon(polygon, label)
      elif list(label)[0] == 'P': # parabola
        self.meander = self.Parabola(polygon, label)
      elif list(label)[0] == 'S': # sqring
       self.meander = self.SquareRing(polygon, label)
      else:
        raise ValueError(f'{label} unknown shape')
      self.shape  = Polygon(polygon)
      self.label  = label
    elif len(xywh) == 4: # defined by cells
      x, y, w, h  = xywh
      self.shape  = Polygon([(x,y), (x,h), (w,h), (w,y)]) # four corners
      self.meander = self.Rectangle(self.shape) # , label)
    else:
      raise ValueError(f"{len(xywh)=} expected 4 or polygon and {label}")


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

'''
the
end
'''
