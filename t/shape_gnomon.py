import unittest
import pprint
from shapely.geometry import Polygon, MultiPolygon
from cell import Layer
from cell.minkscape import *
from cell.shape import Gnomon
from model import SvgWriter
  ##########
  # Gnomon #
  ##########

class Test(unittest.TestCase):

  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.g      = Gnomon()
    self.writer = SvgWriter()
    self.layer  = Layer()
    self.clen   = 18
    self.cells  = minkscape.cells

  def test_a(self, f1=None, f2=None):
  #def test_a(self, facing=None, size=None):
    ''' convert cell dimension for pos n to coords for Shapely.Polygon
    '''
    if f1 is None: f1 = {'facing': 'SW', 'size':'medium' }
    if f2 is None: f2 = {'facing': 'NE', 'size':'small' }
    dim = (0, 6, 6, 12, 2.0, 8.0, 4.0, 10.0, 8.0, 8.0, 10.0, 10.0)
    c1  = self.g.coords(dim, f1['facing'], f1['size'])
    c2  = self.g.coords(dim, f2['facing'], f2['size'])
    mp  = MultiPolygon([Polygon(c1), Polygon(c2)])
    if self.VERBOSE: self.writer.plot(mp, self.id())

  def test_b(self):
    ''' north west gnomon meander 
    '''
    self.test_a(
      f1={'facing': 'NW', 'size':'medium'},
      f2={'facing': 'SE', 'size':'small' }
    )

  def test_c(self, facing='NW'):
    ''' meander using Line class
    '''
    geom           = self.cells['d']['geom']
    dim            = self.layer.dimension(0, 0, self.clen)
    geom['facing'] = facing
    if self.VERBOSE:
      self.pp.pprint(dim)
      self.pp.pprint(geom)

    polyln  = self.g.draw(self.clen, dim[:4], geom)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

  def test_d(self): self.test_c(facing='SW')
  def test_e(self): self.test_c(facing='NE')
  def test_f(self): self.test_c(facing='SE')

  def test_g(self, facing='NW', size='medium'):
    ''' paint gnomons
    '''
    geom           = self.cells['a']['geom']
    dim            = self.layer.dimension(0, 0, self.clen)
    geom['facing'] = facing
    geom['size']   = size
    if self.VERBOSE:
      self.pp.pprint(dim)
      self.pp.pprint(geom)

    polygn  = self.g.paint(dim, geom)
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_h(self): self.test_g(facing='SW')
  def test_i(self): self.test_g(facing='NE', size='small')
  def test_j(self): self.test_g(facing='SE', size='small')
'''
the
end
'''
'''
the
end
'''
