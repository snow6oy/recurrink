import unittest
'''
import pprint
import matplotlib.pyplot as plt
import shapely.plotting
Make, Meander, Spiral  # cell Plotter, Spiral
pp = pprint.PrettyPrinter(indent=2)
'''

from shapely.geometry import Polygon, LinearRing, LineString
from block import Meander
from block.spiral import Spiral
from model import SvgWriter

class Test(unittest.TestCase):
  def setUp(self):
    self.writer  = SvgWriter()
    self.VERBOSE = False

  def test_a(self):
    ''' random sample points with some edge cases
    '''
    s = Spiral()
    assert s.r1( 0, 0, 3)[ 3] == [0, 2]
    assert s.r1( 8, 1, 3)[ 9] == [1, 1]
    assert s.r1(16, 1, 5)[19] == [1, 3]
    assert s.r1( 0, 0, 4)[ 4] == [0, 3]

    assert s.c1( 3, 0, 3)[ 5] == [2, 2]
    assert s.c1(14, 1, 4)[15] == [2, 2]
    assert s.c1( 5, 0, 5)[ 9] == [4, 4]
    assert s.c1(19, 1, 5)[21] == [3, 3]

    assert s.r2( 5, 0, 3)[ 7] == [2, 0]
    assert s.r2( 7, 0, 4)[10] == [3, 0]
    assert s.r2(15, 1, 4)[16] == [2, 1]
    assert s.r2(21, 1, 5)[23] == [3, 1]

    assert s.c2( 7, 0, 3)[ 8] == [1, 0]
    assert s.c2(10, 0, 4)[12] == [1, 0]
    assert s.c2(23, 1, 5)[24] == [2, 1]
    assert s.c2(30, 1, 6)[32] == [2, 1]

  def test_b(self):
    LEN    = 9 # length of matrix 
    s      = Spiral()
    data   = s.matrix(LEN)
    spiral = list(data.values())
    self.assertEqual(81, len(spiral))
    if self.VERBOSE:
      self.writer.plotLine(LineString(spiral), self.id())

  # TODO as feature is frozen
  def test_c(self):
    ''' check spiral line according to the shape of a hole
    '''
    outer  = [(0,0), (9,0), (9,9), (0,9)]
    inner  = [(4,2), (4,7), (7,7), (7,2)]
    small  = Polygon(outer, holes=[inner])
    m      = Meander(small)
    spiral = m.spiral(clen=10, pos=tuple([0,0]))
    if self.VERBOSE:
      self.writer.plotLine(LineString(spiral), self.id())
      '''
      self.assertEqual(2, len(spiral.geoms))
      print(self.id())
      fig, ax = plt.subplots() 
      shapely.plotting.plot_line(spiral, ax=ax, linewidth=0.5)
      plt.savefig(f"tmp/t_meander_o.svg", format="svg")
      '''

  def test_d(self):
    ''' split spiral into many lines according to the shape of a hole
    outer = [(0,0), (3,0), (3,3), (0,3)]
    inner = [(1,1), (1,2), (2,2), (2,1)]
    small = Polygon(outer, holes=[inner])
    m     = Meander(small)
    data  = m.matrix(4)
    line  = list(data.values())
    mls   = m.splitLines(line, Polygon(inner)) #small.interiors[0])
    self.assertEqual(1, len(mls.geoms))
    '''
    pass

  def test_e(self):
    ''' split on a 15 x 15 cell
    '''
    outer = [(0,0), (15,0), (15,15), (0,15)]
    inner = [(5,5), (5,10), (10,10), (10,5)]
    p15   = Polygon(outer, holes=[inner])
    m     = Meander(p15)
    line  = m.spiral(15, tuple([0,0]))

    if self.VERBOSE: self.writer.plotLine(LineString(line), self.id())

    ''' On hold
    l2_begin = list(s.geoms[1].coords)[0]
    self.assertEqual((11,11), l2_begin)

    l2_end   = list(s.geoms[1].coords)[-1]
    self.assertEqual((10,3), l2_end)
    '''

  def test_f(self):
    ''' irregular sqring needs a spiral
    '''
    outer = [(0,0), (60,0), (60,60), (0,60)]
    inner = [(20,15), (20,45), (40,45), (40,15)]
    wonky = Polygon(outer, holes=[inner])
    m     = Meander(wonky)
    data  = m.matrix(60)
    line  = list(data.values())
    split = m.splitLine(line, Polygon(inner)) #small.interiors[0])

    if self.VERBOSE:
      self.writer.plotLine(LineString(split), self.id())


'''
the
end
'''
