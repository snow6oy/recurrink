import unittest
import pprint
from outfile import Layout, Shapes
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class TestLayout(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape '''
    self.ltpx = Layout(scale=1.0, gridsize=1080, cellsize=60)
    self.ltgc = Layout(scale=1.0, gridsize=180, cellsize=24)
    self.positions = config.positions
    self.data = config.cells

  def test_0(self):
    ''' when gridpx / cellsize are small then stroke width will generate negative dimensions
    '''
    self.lt.uniqstyle('d', 'fg', False) 
    self.data['d']['stroke_width'] = 5
    #pp.pprint(self.data['d'])
    g = self.lt.getgroup('fg', 'd')  
    s = Shapes()
    s.cellsize = 3
    self.assertRaises(ValueError, s.foreground, 0, 0, self.data['d'], g)

  def test_1(self):
    ''' small squares are too wonky
    '''
    cs = 24
    sw = 3
    self.lt.uniqstyle('c', 'fg', False) 
    self.data['c']['stroke_width'] = sw
    g = self.lt.getgroup('fg', 'c')  
    s = Shapes()
    s.cellsize = cs
    s.foreground(0, 0, self.data['c'], g)
    '''
    pp.pprint(self.data['c'])
    print(g)
    '''
    x = g[0]['x']
    y = g[0]['y']
    w = g[0]['width']
    h = g[0]['height']
    self.assertEqual(cs, (x + x + w))

'''
the
end
'''
