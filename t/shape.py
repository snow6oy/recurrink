import unittest
from cell import Shape
from config import *

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.data = config.cells
    self.clen = 15 # cell length

  def test_1(self):
    ''' draw a triangle
    '''
    cell_a = self.data['a']
    cell_a['shape'] = 'triangl'
    triangl = Shape('a', cell_a)
    self.assertEqual(triangl.shape.name, 'triangl')
    triangl.shape.draw(0, 0, 0, self.clen, facing='north')
    self.assertEqual(triangl.shape.svg(), '0.0,0.0,15.0,0.0,7.5,15.0,0.0,0.0')
    #triangl.plot()

  def test_2(self):
    ''' circle
    '''
    cell_c = self.data['c']
    cell_c['shape'] = 'circle'
    circle = Shape('c', cell_c)
    self.assertEqual(circle.shape.name, 'circle')
    circle.shape.draw(3, 3, 0, 12, size='large')
    svg = circle.shape.svg()
    self.assertEqual(svg['cx'], 1) # {'cx': 1, 'cy': 1, 'r': 8}
    # circle.plot()

  def test_3(self):
    ''' test defaults 
        square draw x, y, stroke_width, border, size=, facing=
    '''
    square = Shape('a', {'fill':'FFF','fill_opacity':None})
    self.assertEqual(square.shape.name, 'square')
    sw     = self.data['a']['stroke_width']
    f      = self.data['a']['facing']
    s      = self.data['a']['size']
    square.shape.draw(0, 0, 1, self.clen, size=s, facing=f)
    svg = square.shape.svg()
    self.assertEqual(svg['width'], 14.5) 
    #square.plot()

  def test_4(self):
    ''' line
    '''
    line = Shape('b', self.data['b'])
    sw   = self.data['b']['stroke_width']
    f    = self.data['b']['facing']
    s    = self.data['b']['size']
    self.assertEqual(line.shape.name, 'line')
    line.shape.draw(0, 0, 1, self.clen, size=s, facing=f)
    svg  = line.shape.svg()
    self.assertEqual(svg['width'], 5.5) 
    line.plot()

  def test_5(self):
    ''' triangle
    '''
    self.data['d']['shape'] = 'diamond'
    diamond = Shape('d', self.data['d'])
    self.assertEqual(diamond.shape.name, 'diamond')
    diamond.shape.draw(0, 0, 0, self.clen, facing='all')
    coords = list(diamond.shape.data.coords)
    self.assertEqual(coords[-1], (0, 7.5))
    svg = diamond.shape.svg()
    self.assertEqual(svg['points'], '0.0,7.5,7.5,0.0,15.0,7.5,7.5,15.0,0.0,7.5')
    #diamond.plot() 

'''
GEOMINK has inner classes
self.meander = self.Rectangle(polygon)
self.meander = self.Gnomon(polygon, label)
self.meander = self.Parabola(polygon, label)
self.meander = self.SquareRing(polygon, label)
self.meander = self.Irregular(polygon, label)

SHAPE HAS FUNCTIONS
s = self.circle(size, sw, p)
s = self.square(x, y, size, hsw, sw)
s = self.square(x, y, size, hsw, 0)
s = self.line(x, y, facing, size, hsw, sw)
s = self.line(x, y, facing, size, hsw, 0)
s = self.triangle(facing, p)
s = self.diamond(facing, p)
s = self.text(shape, x, y)

triangl x, y, stroke_width, border, facing=, 
circle 	x, y, stroke_width, border, size=
square 	x, y, stroke_width, border, size=, facing=:

the
end
'''
