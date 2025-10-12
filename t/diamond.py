import unittest
import pprint
from cell.shape import Diamond
from cell.minkscape import *
from cell import Layer
from model import SvgWriter

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = True
    self.cell    = minkscape.cells
    self.clen    = 18 # cell length
    self.layer   = Layer()
    self.writer  = SvgWriter()
    self.diamond = Diamond()

  def test_a(self):
    ''' diamond
    '''
    self.cell['d']['geom']['name']   = 'diamond'
    self.cell['d']['geom']['facing'] = 'C'

    points  = self.layer.points(0, 0, 0, self.clen)
    polygn  = self.diamond.coords(points, self.cell['d']['geom'])

    self.assertEqual(self.diamond.name, 'diamond')
    if self.VERBOSE: self.writer.plot(polygn, self.id()) 

  def test_b(self, facing=None):
    ''' meander using Line class
    '''
    points  = self.layer.points(0, 0, 1, self.clen)
    geom    = self.cell['a']['geom']
    if facing: geom['facing'] = facing # override Easterly default
    self.pp.pprint(geom)

    polyln  = self.diamond.draw(points, geom)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

  def test_c(self): self.test_b(facing='N')
  def test_d(self): self.test_b(facing='S')
  def test_e(self): self.test_b(facing='E')
  def test_f(self): self.test_b(facing='W')

'''
the
end
'''
