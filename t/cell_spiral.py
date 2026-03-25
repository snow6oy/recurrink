import unittest
import pprint
from shapely.geometry import Polygon, LinearRing, LineString
from cell.spiral import Spiral
from model import SvgWriter

class Test(unittest.TestCase):
  pp = pprint.PrettyPrinter(indent=2)
  def setUp(self):
    self.writer  = SvgWriter()
    self.VERBOSE = True

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
  def test_z(self):
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
'''
the
end
'''
