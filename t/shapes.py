import unittest
import pprint
from outfile import Layout, Shapes
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class TestShapes(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape '''
    self.lt = Layout(scale=1.0, gridsize=180, cellsize=24)
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
    ''' small squares might become negative 
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

  def test_2(self):
    ''' test a 1080 layout calculates stroke_with and Northern Point for each scale
    '''
    expected_width = [27.5, 55.0, 82.5, 110.0]
    for i, scale in enumerate([0.5, 1.0, 1.5, 2.0]):
      lt = Layout(scale=scale)
      self.data['a']['stroke_width'] = 5
      self.lt.uniqstyle('a', 'fg', False) 
      g = self.lt.getgroup('fg', 'a')  
      lt.foreground(0, 0, self.data['a'], g)
      self.assertEqual(g[-1]['width'], expected_width[i])


  def test_3(self):
    ''' test a 180 layout calculates stroke_with and Northern Point for each scale

0.5     36      30      True    yes     True    1080    True    2.5     15.0
0.5     15      12      True    yes     False   180     True    0.0     6.0
................................................................................
1.0     18      60      True    yes     False   1080    True    5.0     30.0
1.0     8       24      True    yes     False   192     True    0.0     12.0
................................................................................
1.5     12      90      True    yes     False   1080    True    7.5     45.0
1.5     5       36      True    yes     False   180     True    0.0     18.0
................................................................................
2.0     9       120     True    yes     False   1080    True    10.0    60.0
    '''


'''
the
end
'''
