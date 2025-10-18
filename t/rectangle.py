import unittest
import pprint
from cell.minkscape import *
from cell.shape import Rectangle
from cell import Layer
from model import SvgWriter
from shapely.geometry import LineString, Polygon


class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = True
    self.cell    = minkscape.cells
    self.clen    = 9 # cell length
    self.layer   = Layer()
    self.writer  = SvgWriter()
    # dimension of minkscape cell a
    self.dim = [0, 0, 9, 9, 3.0, 3.0, 6.0, 6.0, 12.0, 12.0, 6.0, 6.0]

  def test_a(self):
    ''' rectangle returns a line
    '''
    expect = Polygon(((0, 0), (0, 9), (9, 9), (9, 0)))
    r      = Rectangle('square')
    polygn = Polygon(r.paint(self.dim, minkscape.cells['a']['geom']))
    self.assertEqual(expect, polygn) 
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_b(self, name='square', facing='N', size='medium'):
    ''' meander using Line class
    '''
    geom           = self.cell['b']['geom']
    geom['facing'] = facing 
    geom['name']   = name
    geom['size']   = size
    dim  = self.layer.dimension(0, 0, self.clen)
    r    = Rectangle(name)

    if False:
      self.pp.pprint(dim)
      self.pp.pprint(geom)

    polyln  = r.draw(self.clen, dim, geom)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

  def test_c(self):
    ''' rectangle makes a big square
    '''
    expect = Polygon(((12, 12), (12, 6), (6, 6), (6, 12)))
    r      = Rectangle('square')
    geom   = minkscape.cells['a']['geom']
    geom['size'] = 'large'
    polygn = Polygon(r.paint(self.dim, geom))
    if self.VERBOSE: self.writer.plot(polygn, self.id())
    self.assertEqual(expect, polygn) 

  def test_d(self):
    ''' small square with width
    '''
    self.cell['a']['geom']['size'] = 'small'
    square = Rectangle('square')
    dim    = self.layer.dimension(0, 0, self.clen)
    polygn = square.paint(dim, self.cell['a']['geom'])
    if self.VERBOSE: 
      self.writer.plot(polygn, self.id())

  def test_e(self):
    ''' line
    '''
    line = Rectangle('line')
    self.assertEqual(line.name, 'line')

  def test_f(self): self.test_b(size='small', name='spiral')
  def test_g(self): self.test_b(name='spiral')
  def test_h(self): self.test_b(name='line')
  def test_i(self): self.test_b(name='line', facing='E')
  def test_j(self): self.test_b(facing='C')

'''
the
end
'''
