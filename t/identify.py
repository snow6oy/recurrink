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

  def test_a(self):
    ''' square all 
    '''
    p = Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
    name =  self.cell_a.bless(p)
    self.assertEqual('rectangle', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('square', name)
    self.assertEqual('all', facing)

  def test_b(self):
    ''' line east
    '''
    p = Polygon([(2, 1), (2, 2), (7, 2), (7, 1), (2, 1)])
    name =  self.cell_a.bless(p)
    self.assertEqual('rectangle', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('line', name)
    self.assertEqual('east', facing)

  def test_c(self):
    ''' wrong type
    '''
    lr = LinearRing([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
    self.assertRaises(NotImplementedError, self.cell_a.bless, lr)

  def test_d(self):
    ''' gnomon nw 
    '''
    p = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0), (0, 0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('gnomon', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('NW', facing)

  def test_e(self):
    ''' gnomon se 
    '''
    p = Polygon([(1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 0), (1, 0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('gnomon', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('SE', facing)

  def test_f(self):
    ''' parabola n
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    name =  self.cell_a.bless(p)
    self.assertEqual('parabola', name)
    name, facing = self.cell_a.direct(name, p)
    self.assertEqual('north', facing)

  def test_g(self):
    ''' can you tell if I am a parabola that can be meandered
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    a = CellMaker((0,0), clen=3)
    self.assertTrue(a.parabola(p))

  def test_h(self):
    ''' same test as above but with identify
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    a = CellMaker((0,0), clen=3)
    self.assertEqual('parabola', a.bless(p))

  def test_i(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    a = CellMaker((0,0), clen=3)
    self.assertFalse(a.parabola(p))

  def test_j(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    a = CellMaker((0,0), clen=3)
    self.assertEqual('irregular', a.bless(p))

  def test_k(self):
    ''' test is ok but no points are removed !
        shapely.extract_unique_points(geometry)
        shapely.remove_repeated_points.html#shapely.remove_repeated_points
    '''
    lr = LinearRing([(0,0),(0,1),(0,1),(0,2),(0,3),(3,3),(3,0)])
    a  = CellMaker((0,0), clen=4)
    tr = a.trimPoints(lr)
    self.assertEqual(7, len(list(tr.coords)))

  def test_l(self): 
    ''' sqring with wonky holes are irregular
    '''
    outer = [(0,0), (60,0), (60,60), (0,60)]
    inner = [(20,15), (20,45), (40,45), (40,15)]
    wonky = Polygon(outer, holes=[inner])
    self.assertEqual('irregular', self.cell_a.bless(wonky))

  def test_m(self):
    ''' happy path for sqring
    '''                     
    outer = [(0,0), (60,0), (60,60), (0,60)]
    inner = [(20,20), (20,40), (40,40), (40,20)]
    okay  = Polygon(outer, holes=[inner])
    self.assertTrue(self.cell_a.sqring(okay))



'''
the
end
'''

