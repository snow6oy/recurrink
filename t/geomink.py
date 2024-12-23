import unittest
import pprint
from shapely.geometry import Polygon
from shapes import Geomink
from fl8n import Plotter
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    pass

  def test_1(self):
    ''' rectangle
    '''
    r     = Polygon([(1, 1), (1, 2), (2, 2), (2, 1)])
    gmk   = Geomink(polygon=r)
    shape = gmk.shapeTeller('rectangle')
    self.assertTrue(shape)

  def test_2(self):
    ''' gnomon
    '''
    g = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0)])
    gmk   = Geomink(polygon=g)
    shape = gmk.shapeTeller('gnomon')
    self.assertTrue(shape)

  def test_3(self):
    ''' parabola
    '''
    pb = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 1), (3, 1), (3, 0)])
    gmk   = Geomink(polygon=pb)
    shape = gmk.shapeTeller('parabola')
    self.assertTrue(shape)

  def test_4(self):
    ''' square ring
    '''
    hole  = [(1, 1), (1, 2), (2, 2), (2, 1)]
    outer = [(0, 0), (0, 3), (3, 3), (3, 0)]
    sr    = Polygon(outer, holes=[hole])
    gmk   = Geomink(polygon=sr)
    shape = gmk.shapeTeller('sqring')
    self.assertTrue(shape)

  def test_5(self):
    ''' dangling extra points
        when shapely operations leave dangling points simplify MIGHT tidy up, e.g.

        clean = polygon.boundary.simplify(tolerance=1)

        but it has unacceptable side-effect of clobbering Gnomons and Parabolas
        this test documents the risk of shapeTeller being fooled by the danglers
    '''
    r     = Polygon([(0, 0), (0, 1), (0, 3), (3, 3), (3, 0)])
    self.assertRaises(ValueError, Geomink, polygon=r)

'''
the
end
'''
