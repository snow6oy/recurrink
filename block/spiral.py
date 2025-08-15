'''
import pprint
pp = pprint.PrettyPrinter(indent=2)
import math
import matplotlib.pyplot as plt
from shapely import line_merge, set_precision
)
'''
from shapely.geometry import Point, LineString, MultiLineString, Polygon

class Spiral:
  '''
  1 2 3     
  8 9 4
  7 6 5

   1  2  3  4
  12 13 14  5
  11 16 15  6
  10  9  8  7

   1  2  3  4  5      1  2  3  4  5  6
  16 17 18 19  6     20 21 22 23 24  7
  15 24 25 20  7     19 32 33 34 25  8
  14 23 22 21  8     18 31 36 35 26  9
  13 12 11 10  9     17 30 29 28 27 10
                     16 15 14 13 12 11
  '''
  VERBOSE = False

  def spiral(self, clen, pos):
    ''' split a LineString and return a MultiLineString
        split on boundary of Polygon.interiors[0]
    '''
    x, y, w, h = self.shape.bounds
    clen       = int(w - x)     # better than original clen because of padding
    pos        = tuple([x, y])  # better than pos because of tx
    db   = self.matrix(clen)
    # self.prettyPrint(clen, db)
    line = self.offset(clen, pos, list(db.values()))
    ''' this is returning positions with an extra clen
        without holes there will be overlaps /-:
    '''
    if len(self.shape.interiors) == 1: 
      if self.shape.interiors[0].geom_type != 'LinearRing':
        raise ValueError()
      else:
        hole = self.shape.interiors[0]
        line = self.splitLine(line, hole) #Polygon(hole))
    return line

    '''
    print(f"{clen} {pos} {len(self.shape.interiors)=}")
    return line 
        return mls 
    else:
      raise IndexError(f"{len(self.shape.interiors)=} is not one")
    return MultiLineString([LineString(line)]) 
    '''

  def offset(self, clen, pos, points):
    ''' CellMaker increases pos by the factor of cell length
    '''
    X = pos[0]
    Y = pos[1]
    offset = [tuple([X + p[0], Y + p[1]]) for p in points]
    return offset

  def splitLine(self, line, hole):
    ''' test line using touches and contains 
        split when spiral passes inside hole
    '''
    new_line = []
    for xy in line:
      pt = Point(xy)
      new_line.append(xy)
      # print(f"{hole.contains(pt)=} {len(new_line)=} {xy}")
      if hole.contains(pt): break
    return new_line

  def __splitLines(self, line, hole):
    ''' test line using touches and contains 
        split when spiral passes inside hole
    '''
    inside   = False
    mls      = []
    new_line = []
    for xy in line:
      pt = Point(xy)
      print(f"{hole.touches(pt)=} {inside=} {xy}")
      if hole.touches(pt) and inside: pass
      elif hole.touches(pt):
        new_line.append(xy)
        if hole.contains(LineString(new_line)): 
          inside  = True
        else:
          mls.append(LineString(new_line))
          inside  = True
      elif inside:
        new_line = []
        new_line.append(xy)
        inside   = False
      else:
        new_line.append(xy)
    return MultiLineString(mls)

  def prettyPrint(self, clen, db):
    ''' its borken
    '''
    m  = [[0]*clen for i in range(clen)] # output template
    for k in db:   # convert to printer friendly format
      print(k)
      r = db[k][0]
      c = db[k][1]
      m[r][c] = f"{k:02d}"
      [print(" ".join(s)) for s in m]

  def matrix(self, LEN):
    ''' call rows 1, 2 and col 1, 2 and pack points into a list
    '''
    count = 0  # final number of cells
    n     = 0  # depth of spiral
    db    = {} # temp data collection

    for n in range(LEN):
      db = {**db, **self.r1(count, n, LEN)} # append top rows
      count = max(db.keys())           # track last item
      if (count == LEN * LEN): break   # are we there yet?

      db = {**db, **self.c1(count, n, LEN)} # right hand cols
      count = max(db.keys())

      db = {**db, **self.r2(count, n, LEN)} # bottom rows
      count = max(db.keys())
      if (count >= LEN * LEN): break

      db = {**db, **self.c2(count, n, LEN)} # left hand col
      count = max(db.keys())

    return db


  def r1(self, s, n, l):
    ''' x x x 
        o o o
        o o o 
    n+1 to LEN-n '''
    line = {}
    A = x = n
    B = l - n
    if self.VERBOSE: print("A={} B={} x={} END={}".format(A, B, x, (l * l))) 

    for y in range(A, B):
      s += 1 
      if s > (l * l): break
      if self.VERBOSE: print("r1 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def c1(self, s, n, l):
    ''' o o o
        o o x
        o o o
    n+1 to LEN-n '''
    line = {}
    A = n + 1
    B = l - n
    y = l - n - 1
    if self.VERBOSE: print("A={} B={} y={}".format(A, B, y)) 
    for x in range(A, B):
      s += 1 
      if s > (l * l): break
      if self.VERBOSE: print("c1 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def r2(self, s, n, l):
    ''' o o o
        o o o
        x x x 
    LEN-n+1 to n '''
    line = {}
    A = l - (n + 2)
    x = l - (n + 1)
    B = n - 1
    if self.VERBOSE: print("A={} B={} x={}".format(A, B, x)) 
    for y in range(A, B, -1):  # 1, -1
      s += 1
      if s > (l * l): break
      if self.VERBOSE: print("r2 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

  def c2(self, s, n, l):
    ''' o o o
        x o o
        o o o
    LEN-n+1 to n '''
    line = {}
    A = l - (n + 2)
    y = n
    B = n
    if self.VERBOSE: print("A={} B={} y={}".format(A, B, y)) 
    for x in range(A, B, -1):
      s += 1
      if self.VERBOSE: print("c2 {}={},{}".format(s, x, y)) 
      line[s] = [x, y]
    return line

'''
the
end
'''
