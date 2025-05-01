import unittest
import pprint
from cell.geomink import Plotter
from cell.cellmaker import CellMaker
from shapely.geometry import Polygon, LinearRing
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.VERBOSE = True
    self.writer  = Plotter()
    clen         = 3
    self.cell_a  = CellMaker((0, 0), clen) 

  def test_1(self):
    ''' square all 
    '''
    p = Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
    name =  self.cell_a.bless(p)
    self.assertEqual('rectangle', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('square', name)
    self.assertEqual('all', facing)

  def test_2(self):
    ''' line east
    '''
    p = Polygon([(2, 1), (2, 2), (7, 2), (7, 1), (2, 1)])
    name =  self.cell_a.bless(p)
    self.assertEqual('rectangle', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('line', name)
    self.assertEqual('east', facing)

  def test_3(self):
    ''' wrong type
    '''
    lr = LinearRing([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
    self.assertRaises(NotImplementedError, self.cell_a.bless, lr)

  def test_4(self):
    ''' 
    '''
    pass

  def test_5(self):
    ''' gnomon nw 
    '''
    p = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0), (0, 0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('gnomon', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('NW', facing)

  def test_6(self):
    ''' gnomon se 
    '''
    p = Polygon([(1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 0), (1, 0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('gnomon', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('SE', facing)

  def test_7(self):
    ''' parabola n
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('parabola', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('north', facing)

  def test_8(self): pass

  def test_9(self):
    ''' can shapeTeller tell if I am a parabola that can be meandered
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    a = CellMaker((0,0), clen=3)
    self.assertTrue(a.shapeTeller(p, 'parabola'))

  def test_10(self):
    ''' same test as above but with identify
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    a = CellMaker((0,0), clen=3)
    self.assertEqual('parabola', a.bless(p))

  def test_11(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    a = CellMaker((0,0), clen=3)
    self.assertFalse(a.shapeTeller(p, 'parabola'))

  def test_12(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    a = CellMaker((0,0), clen=3)
    self.assertEqual('irregular', a.bless(p))

'''
the
end
'''
