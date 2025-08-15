import unittest
from config import *
from cell.shape import Rectangle
from model import SvgWriter
from shapely.geometry import LineString, Polygon

class Test(unittest.TestCase):

  def setUp(self):
    self.writer = SvgWriter()
    self.VERBOSE = True
    # dimension of minkscape cell a
    self.dim = [0, 0, 9, 9, 3.0, 3.0, 6.0, 6.0, 12.0, 12.0, 6.0, 6.0]

  def test_a(self):
    ''' rectangle returns a line
    '''
    expect = Polygon(((0, 0), (0, 9), (9, 9), (9, 0)))
    r      = Rectangle('square')
    polygn = Polygon(r.coords(self.dim, config.cells['a']['geom']))
    self.assertEqual(expect, polygn) 
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_b(self):
    ''' rectangle square has a spiral guide
    '''
    r     = Rectangle('square')
    guide = r.guide('all')
    self.assertEqual('spiral', guide[0])

'''
the
end
'''
