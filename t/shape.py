import unittest
from cell import Shape
from config import *

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = False
    self.data    = config.cells
    self.clen    = 15 # cell length

  def test_a(self):
    ''' circle
    '''
    cell_c          = self.data['c']
    cell_c['shape'] = 'circle'
    cell_c['size']  = 'large'
    circle = Shape('c', cell_c)
    self.assertEqual(circle.this.name, 'circle')

    circle.draw(3, 3, 12)
    svg = circle.svg()
    self.assertEqual(svg['cx'], 1) # {'cx': 1, 'cy': 1, 'r': 8}
    if self.VERBOSE: circle.plot()

  def test_b(self):
    ''' small square with width
    '''
    square = Shape('c', {'stroke_width':1, 'size':'small'})
    square.draw(0, 0, 12)
    svg = square.svg()
    self.assertEqual(svg['width'], 4) 
    if self.VERBOSE: square.plot()

  def test_c(self):
    ''' draw a triangle
    '''
    cell_a           = self.data['a']
    cell_a['shape']  = 'triangl'  # override
    cell_a['facing'] = 'north'
    triangl          = Shape('a', cell_a)
    self.assertEqual(triangl.this.name, 'triangl')

    triangl.draw(0, 0, self.clen)
    svg = triangl.this.svg()
    if self.VERBOSE: triangl.plot()
    self.assertEqual('0.0,0.0,15.0,0.0,7.5,15.0,0.0,0.0', svg['points'])

  def test_d(self):
    ''' line
    '''
    self.data['b']['stroke_width'] = 1
    line = Shape('b', self.data['b'])
    self.assertEqual(line.this.name, 'line')

    line.draw(0, 0, self.clen)  #, size=s, facing=f)
    svg  = line.svg()
    self.assertEqual(svg['width'], 4) 
    if self.VERBOSE: line.plot()

  def test_e(self):
    ''' diamond
    '''
    self.data['d']['shape']  = 'diamond'
    self.data['d']['facing'] = 'all'
    diamond = Shape('d', self.data['d'])
    self.assertEqual(diamond.this.name, 'diamond')
    diamond.draw(0, 0, 16)
    if self.VERBOSE: diamond.plot() 
    coords = list(diamond.this.data.boundary.coords)
    self.assertEqual(coords[-1], (0, 8))
    svg = diamond.svg()
    self.assertEqual(
      '0.0,8.0,8.0,0.0,16.0,8.0,8.0,16.0,0.0,8.0', svg['points']
    )

  def test_f(self):
    ''' transform a triangle
    '''
    triangl = Shape('a', {'shape': 'triangl','facing':'north'})
    triangl.draw(0, 0, self.clen)
    self.assertTrue(triangl.this.data.is_valid)
    # TODO throws MultiPoint error
    t2 = triangl.tx(15, 0)
    self.assertEqual(15, triangl.this.data.bounds[0])

'''
the
end
'''
