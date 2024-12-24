import unittest
import pprint
from shapes import Geomink, Plotter
from flatten import Flatten
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.f = Flatten()

  def test_1(self):
    ''' does shapely return the expected boundary for our rectangle
    '''
    expect = ([[2, 2, 4, 4, 2], [2, 4, 4, 2, 2]])
    gmk = Geomink(xywh=(2, 2, 4, 4))
    xy = list(gmk.shape.boundary.xy)
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

'''
the
end
'''
