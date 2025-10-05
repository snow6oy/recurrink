import unittest
import pprint
from shapely.geometry import Polygon, LineString
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
    self.clen    = 12

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

  def test_j(self):
    ''' join stripes 
        missing case where gnomon and edge lines
        only intersect at their tail ends
    '''
    gnomon = LineString([
      (0, 0),
      (0, 8),
      (8, 8),
      (8, 7),
      (1, 7),
      (1, 0),
      (2, 0),
      (2, 6)
    ])
    edge = LineString([
      (5, 6),
      (5, 0),
      (6, 0),
      (6, 6),
      (7, 6),
      (7, 0),
      (8, 0),
      (8, 6)
    ])
    polyln = self.p.joinStrings(gnomon, edge)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

'''
the
end
'''
