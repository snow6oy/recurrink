import unittest
import pprint
from cell.shape import *
from cell.minkscape import *
from cell import Layer
from model import SvgWriter

class Test(unittest.TestCase):
  VERBOSE = True
  pp      = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.cell   = minkscape.cells
    self.clen   = 18 # cell length
    self.circle = Circle() # 'c', cell_c)
    self.layer  = Layer()
    self.writer = SvgWriter()

  def test_a(self):
    ''' circle
    '''
    self.assertEqual(self.circle.name, 'circle')

  def test_b(self):
    ''' polygon
    '''
    geom         = self.cell['c']['geom']
    geom['name'] = 'circle'
    geom['size'] = 'large'
    x, y, stroke_width, clen = 3, 3, 0, self.clen
    points = self.layer.points(x, y, stroke_width, self.clen)
    polygn = self.circle.paint(points, geom)
    self.assertEqual('Polygon', polygn.geom_type)
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_c(self, size='medium'):
    ''' linear circles
    '''
    points  = self.layer.points(0, 0, 0, self.clen)
    geom    = self.cell['c']['geom']
    if size: geom['size'] = size
    #self.pp.pprint(geom)

    polyln  = self.circle.draw(points, geom)
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())

  def test_d(self): self.test_c(size='small')
  def test_e(self): self.test_c(size='large')

  def test_f(self):
    ''' concentric (unused but nice)
    '''
    points  = self.layer.points(0, 0, 0, self.clen)
    geom    = self.cell['c']['geom']
    polyln  = self.circle.drawConcentric(points, geom)
    '''
    for g in polyln.geoms:
      print(g.geom_type)
    '''
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())
  
'''
the
end
'''
