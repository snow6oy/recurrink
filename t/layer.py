''' source v/bin/activate
    python -m unittest t.Test.test_n
'''
import unittest
import pprint
from cell import Layer
from config import *
from model import SvgWriter, SvgLinear
from shapely.geometry import LinearRing, Polygon, MultiPolygon
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.VERBOSE = False
    self.writer  = SvgWriter()

  def test_a(self):
    ''' create a simple with bg and fg
    '''
    cell = Layer()
    cell.background()
    cell.foreground(
      shape=config.cells['a']['shape'],
      size=config.cells['a']['size'],
      facing=config.cells['a']['facing']
    )
    p1 = cell.polygon()
    p2 = cell.tx(9, 0)
    mp = MultiPolygon([p1.geoms, p2.geoms])
    if self.VERBOSE: self.writer.plot(mp, self.id())


  def test_b(self):
    ''' test exploder walks the grid
    '''
    a0      = LinearRing(((0,0), (0,9), (9,9), (9,0)))
    a1      = LinearRing(((4,4), (4,6), (6,6), (6,4)))
    a       = Polygon(a0, holes=[a1])
    b       = Polygon(((9,0), (9,9), (18,5)))
    c       = Polygon(((0,15), (9,18), (9,9)))
    d       = Polygon(((9,9), (9,18), (18,18), (18,9)))
    block   = [a, b, c, d]
    CLEN    = 9
    b0, b1  = (2, 2)  # blocksize
    gsize   = 3
    edge    = gsize * CLEN

    svglin  = SvgLinear(CLEN)
    model   = svglin.walk(block, gsize, b0, b1, CLEN, edge)
    mp      = MultiPolygon(model)
    if self.VERBOSE: self.writer.plot(mp, self.id())

  def test_c(self):
    ''' set clock migrated from Parabola
    '''
    l = Layer()
    self.assertFalse(l.setClock())  #12.0, 12.0))

'''
the
end
'''
