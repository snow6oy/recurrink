import unittest
from cell.minkscape import *
from cell.shape import Rectangle
from model import SvgWriter
from shapely.geometry import LineString, Polygon

class Test(unittest.TestCase):

  def setUp(self):
    self.writer = SvgWriter()
    self.VERBOSE = False
    # dimension of minkscape cell a
    self.dim = [0, 0, 9, 9, 3.0, 3.0, 6.0, 6.0, 12.0, 12.0, 6.0, 6.0]

  def test_a(self):
    ''' rectangle returns a line
    '''
    expect = Polygon(((0, 0), (0, 9), (9, 9), (9, 0)))
    r      = Rectangle('square')
    polygn = Polygon(r.coords(self.dim, minkscape.cells['a']['geom']))
    self.assertEqual(expect, polygn) 
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_b(self):
    ''' rectangle square has a spiral guide
    '''
    r     = Rectangle('square')
    guide = r.guide('C')
    self.assertEqual('spiral', guide[0])

  def test_c(self):
    ''' rectangle makes a big square
    '''
    expect = Polygon(((12, 12), (12, 6), (6, 6), (6, 12)))
    r      = Rectangle('square')
    geom   = minkscape.cells['a']['geom']
    geom['size'] = 'large'
    polygn = Polygon(r.coords(self.dim, geom))
    if self.VERBOSE: self.writer.plot(polygn, self.id())
    self.assertEqual(expect, polygn) 

'''
the
end
'''
