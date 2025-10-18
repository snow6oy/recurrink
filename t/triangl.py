import unittest
import pprint
from cell.shape import Triangle
from cell.minkscape import *
from cell import Layer
from model import SvgWriter
from block import Meander

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = True
    self.cell    = minkscape.cells
    self.clen    = 18 # cell length
    self.triangl = Triangle()
    self.layer   = Layer()
    self.writer  = SvgWriter()

  def test_a(self, guide=False):
    ''' draw a triangle
    '''
    self.assertEqual(self.triangl.name, 'triangl')
    geom   = self.cell['d']['geom']
    points = self.layer.points(0, 0, 1, self.clen)
    polygn = self.triangl.paint(points, geom)

    self.assertEqual(1, points[0])
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_b(self): pass
    
  def test_c(self): self.test_f(facing='N')
  def test_d(self): self.test_f(facing='S')
  def test_e(self): self.test_f(facing='W')

  def test_f(self, facing=None):
    ''' prototype meander Line class
    '''
    points  = self.layer.points(0, 0, 1, self.clen)
    geom    = self.cell['d']['geom']
    if facing: geom['facing'] = facing # override Easterly default
    #self.pp.pprint(geom)

    polyln  = self.triangl.draw(points, geom)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())


'''
the
end
'''
