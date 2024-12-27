import unittest
import pprint
from shapes import Geomink, Plotter
from flatten import Flatten
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.f = Flatten()
    self.writer = Plotter()

  def test_1(self):
    ''' east square linefill for Rectangle.meander()
    '''
    expect = [ 
      (2, 2), (6, 2), (6, 3), (2, 3), (2, 4), (6, 4), (6, 5), (2, 5), (2, 6), (6, 6)
    ]
    gmk = Geomink(xywh=(1, 1, 7, 7))
    xy = gmk.meander.fill(direction='E')
    self.assertEqual(expect, list(xy.coords)) 
    self.writer.plotLine(xy, fn='rectangle_1')

  def test_2(self):
    ''' north square
    '''
    expect = [ 
      (1,1),(1,8),(2,8),(2,1),(3,1),(3,8),(4,8),(4,1),
      (5,1),(5,8),(6,8),(6,1),(7,1),(7,8),(8,8),(8,1)
    ]
    gmk = Geomink(xywh=(0, 0, 9, 9))
    xy = gmk.meander.fill(direction='N')
    self.assertEqual(expect, list(xy.coords))
    self.writer.plotLine(xy, fn='rectangle_2')

'''
the
end
'''
