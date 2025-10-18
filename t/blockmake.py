import unittest
import pprint
from shapely.geometry import MultiPolygon, Polygon
from block import Make
from cell.minkscape import *

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)
  def setUp(self):
    self.VERBOSE = False

  def test_a(self):
    ''' make cell and check style
    '''
    bm = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('#F00', bm.style.fill[(0,0)][0])

  def test_b(self):
    ''' cell geoms are kept in block1
    '''
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual(9.0, bm.cells[(0,0)].geoms[0].bounds[-1])

  def test_c(self):
    ''' cells made with Shapely have direction
    '''
    bm = Make(linear=True)
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('MultiLineString', bm.cells[(0,0)].geom_type)

  def test_d(self):
    ''' test type
    '''
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    cell    = bm.cells[0,0]
    self.assertEqual('MultiPolygon', cell.geom_type)

  def test_e(self):
    ''' svg coords for each minkscape cell
    '''
    expected = [
      (0, 0), (9, 0), (18, 0), (0, 0), (12, 0), (21, 3), (3, 3), (6, 3)
    ]
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    to_test = list()
    for z in range(3):
      for pos in bm.cells:
        polygn = bm.polygon(pos, z)
        if polygn:
          x, y, *zz = polygn.bounds
          to_test.append(tuple([int(x), int(y)]))
    if self.VERBOSE: pp.pprint(to_test)
    self.assertEqual(len(expected), len(to_test))
    [self.assertEqual(e, to_test[i]) for i, e in enumerate(expected)]
'''
the 
end
'''
