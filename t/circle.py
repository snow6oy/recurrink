import unittest
from cell.shape import *
from cell.minkscape import *
from cell import Layer

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = False
    self.cell    = minkscape.cells
    self.clen    = 9 # cell length
    self.layer  = Layer()

  def test_a(self):
    ''' circle
    '''
    circle = Circle() # 'c', cell_c)
    self.assertEqual(circle.name, 'circle')

  def test_b(self):
    geom         = self.cell['c']['geom']
    geom['name'] = 'circle'
    geom['size'] = 'large'
    circle = Circle() # 'c', cell_c)
    x, y, stroke_width, clen = 3, 3, 0, 9
    points = self.layer.points(x, y, stroke_width, clen)
    polygn = circle.coords(points, geom)
    self.assertEqual('Polygon', polygn.geom_type)

'''
the
end
'''
