import unittest
import pprint
from shapely.geometry import Polygon
from cell.shape import Parabola
from cell import Layer
from model import SvgWriter
############
# Parabola #
############

class Test(unittest.TestCase):

  VERBOSE = True
  pp      = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.p       = Parabola()
    self.layer   = Layer()
    self.writer  = SvgWriter()
    self.clen    = 36

  def test_a(self):
    ''' start simple
    '''
    self.assertEqual(self.p.name, 'parabola')

  def test_b(self, facing='S'):
    ''' south parabola contructs ok with cell length 15
    '''
    kwargs = {'facing': facing, 'size': 'medium'}
    dim    = (0, 0, 14, 14, 5, 5, 10, 10)
    coords = self.p.coords(dim, kwargs)
    if self.VERBOSE: self.writer.plot(Polygon(coords), self.id())

  def test_c(self): self.test_b(facing='W')
  def test_d(self): self.test_b(facing='N')
  def test_e(self): self.test_b(facing='E')

  def test_f(self, facing='W', ccw=False):
    ''' west meander CCW = False
    '''
    dim    = self.layer.dimension(0, 0, self.clen)
    #self.pp.pprint(dim)

    polyln = self.p.draw(facing, self.clen, dim)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

  def test_g(self): self.test_f(facing='N')
  def test_h(self): self.test_f(facing='S')
  def test_i(self): self.test_f(facing='E')

'''
the
end
'''
