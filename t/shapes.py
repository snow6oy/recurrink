import unittest
import pprint
from model import Layout
from cell import Shapes
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape '''
    self.lt        = Layout(scale=1.0, gridsize=180, cellsize=24)
    self.shapes    = Shapes(scale=1.0, cellsize=24)
    self.positions = config.positions
    self.data      = config.cells

  def test_0(self):
    ''' does shape calculate width without trailing zeros
    '''
    self.data['a']['stroke_width'] = 5
    shape = self.shapes.foreground(0, 0, self.data['a'])
    self.assertEqual(shape['width'], 19)

  ''' when gridpx / cellsize are small then stroke width will generate negative dimensions
  def test_1(self):
    self.data['d']['stroke_width'] = 5
    #pp.pprint(self.data['d'])
    self.shapes.cellsize = 3
    self.assertRaises(ValueError, self.shapes.foreground, 0, 0, self.data['d'])
  '''

  def test_2(self):
    ''' small squares might become negative 
    '''
    self.data['c']['stroke_width'] = 3
    sq = self.shapes.foreground(0, 0, self.data['c'])
    '''
    pp.pprint(self.data['c'])
    print(sq)
    '''
    x = sq['x']
    y = sq['y']
    w = sq['width']
    self.assertEqual(self.lt.cellsize, (x + x + w))

  def test_3(self):
    ''' how does a 1080 layout calculate stroke_width for each scale
    expected_width = [27.5, 41.25, 55.0, 82.5, 110.0]
    '''
    expected_width = [21.5, 20.25, 19.0, 16.5, 14.0]
    for i, scale in enumerate([0.5, 0.75, 1.0, 1.5, 2.0]):
      lt = Layout(scale=scale)
      shapes = Shapes(scale=scale, cellsize=24)
      self.data['a']['stroke_width'] = 5
      fg = shapes.foreground(0, 0, self.data['a'])
      self.assertEqual(fg['width'], expected_width[i])

  def test_4(self):
    ''' test 180 layout calculates stroke_with and Northern Point for each scale
    expected_width = [9.5, 14.25, 19.0, 28.5, 38.0]
    '''
    expected_width = [21.5, 20.25, 19.0, 16.5, 14.0]
    for i, scale in enumerate([0.5, 0.75, 1.0, 1.5, 2.0]):
      lt = Layout(scale=scale, gridsize=180, cellsize=24)
      shapes = Shapes(scale=scale, cellsize=24)
      self.data['a']['stroke_width'] = 5
      fg = shapes.foreground(0, 0, self.data['a'])
      self.assertEqual(fg['width'], expected_width[i])

  def test_5(self):
    ''' bad size 
    '''
    geometry = {
      'shape':'square',
      'size':'tiny',      # wrong!
      'facing':'north',
      'stroke_width': 0
    }
    with self.assertRaises(ValueError):
      self.shapes.foreground(x=0, y=0, cell=geometry)

'''
the
end
'''
