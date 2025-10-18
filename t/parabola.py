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
    ''' start simple who am i ?
    '''
    self.assertEqual(self.p.name, 'parabola')
    dim    = (0, 0, 270, 270, 90, 90, 180, 180)
    polygn = self.p.paint(dim, {'facing': 'N'})
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_b(self, facing='S'):
    ''' south parabola contructs ok with cell length 15
    '''
    dim    = (0, 0, 14, 14, 5, 5, 10, 10)
    coords = self.p.coords(dim, facing)
    if self.VERBOSE: self.writer.plot(Polygon(coords), self.id())

  def test_c(self): self.test_b(facing='W')
  def test_d(self): self.test_b(facing='N')
  def test_e(self): self.test_b(facing='E')

  def test_f(self, facing='W', ccw=False):
    ''' default meander is west meander
    '''
    dim    = self.layer.dimension(0, 0, self.clen)
    polyln = self.p.draw(self.clen, dim, {'facing': facing})
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
      (2, 6),
      (2, 0),
      (1, 0),
      (1, 7),
      (8, 7),
      (8, 8),
      (0, 8),
      (0, 0)
    ])
    edge = LineString([
      (6, 6),
      (6, 0),
      (7, 0),
      (7, 6),
      (8, 6),
      (8, 0)
    ])
    polyln = self.p.joinStrings(gnomon, edge)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

'''
the
end
'''
