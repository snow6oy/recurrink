import unittest
from cell.shape import Triangle
from cell.minkscape import *
from cell import Layer
from model import SvgWriter

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = True
    self.cell    = minkscape.cells
    self.clen    = 9 # cell length
    self.triangl = Triangle()
    self.layer   = Layer()
    self.writer  = SvgWriter()

  def test_a(self, guide=False):
    ''' draw a triangle
    '''
    self.assertEqual(self.triangl.name, 'triangl')
    cell_d           = self.cell['d']
    cell_d['name']   = 'triangl'  # override
    cell_d['facing'] = 'N'
    points           = self.layer.points(0, 0, 1, self.clen)
    polygn           = self.triangl.coords(points, cell_d)

    self.assertEqual(1, points[0])
    if self.VERBOSE: self.writer.plot(polygn, self.id())
    if guide: 
      g = self.triangl.guide(cell_d['facing'])
      self.assertTrue('border' in g)

  def test_b(self):
    ''' check a triangle guide
    '''
    self.test_a(guide=True)
'''
the
end
'''
