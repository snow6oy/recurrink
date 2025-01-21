import unittest
import pprint
from cell.geomink import Geomink, Plotter
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def test_1(self):
    ''' does shapely return the expected boundary for our rectangle
    '''
    expect = ([[2, 2, 4, 4, 2], [2, 4, 4, 2, 2]])
    gmk = Geomink(cellsize=15, xywh=(2, 2, 4, 4))
    xy = list(gmk.shape.boundary.xy)
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_2(self):
    ''' create geomink from cell db 
    '''
    gmk = Geomink(cellsize=15, layer='bg', cell={'bg':'000'}, coord=(2, 2))
    self.assertTrue(gmk.shape.bounds, (2.0, 2.0, 17.0, 17.0))

'''
the
end
'''
