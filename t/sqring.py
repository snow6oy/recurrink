import unittest
import pprint
from shapely.geometry import Polygon, MultiLineString
from cell import Shape, Plotter, CellMaker
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.writer = Plotter()
    self.VERBOSE = False

  def test_a(self):
    ''' sqring meander
    '''
    a     = Shape('a', {'shape': 'sqring','facing':'all'})
    hole  = [(5, 5), (5, 10), (10, 10), (10, 5)]
    outer = [(0, 0), (0, 15), (15, 15), (15, 0)]
    p     = Polygon(outer, holes=[hole])
    self.assertFalse(a.compute(p)) # only returns new Polygon when hole is bad
    line  = a.this.lineFill(facing=a.facing) # bypass Shape.svg()
    self.assertEqual((5,0), list(line.coords)[0])
    if self.VERBOSE: 
      self.writer.plotLine(line, fn='t_sqring_a')

  def test_b(self):
    ''' from koto cell c
        1. detect fault
    '''
    outer= [(14.0, 29.0), (14.0, 16.0), (1.0, 16.0), (1.0, 29.0), (14.0, 29.0)]
    hole = [(9.0, 22.0), (7.0, 22.0), (7.0, 24.0), (9.0, 24.0), (9.0, 22.0)]
    b  = Shape('a', {'shape': 'sqring','facing':'all'})
    p  = Polygon(outer, holes=[hole])
    self.assertTrue(b.compute(p))

  def test_c(self):
    ''' from koto cell c
        2. test remedy
    '''
    outer = [(14.0, 29.0), (14.0, 16.0), (1.0, 16.0), (1.0, 29.0),(14.0, 29.0)]
    hole = [(9.0, 22.0), (7.0, 22.0), (7.0, 24.0), (9.0, 24.0), (9.0, 22.0)]
    # good [(9.0, 21.0), (7.0, 21.0), (7.0, 23.0), (9.0, 23.0), (9.0, 21.0)]
    b  = Shape('a', {'shape': 'sqring','facing':'all'})
    p  = Polygon(outer, holes=[hole])
    if b.compute(p): # return True means the bad hole was silently fixed
      line  = b.this.lineFill(facing=b.facing)
      if self.VERBOSE: self.writer.plotLine(line, fn='t_sqring_c')
      self.assertEqual(36, len(list(line.coords)))
    else:
      self.assertFalse(True) # fail as bad hole went undetected

  def test_d(self):
    ''' eflat cell f made a sqring flattened from a small line
    '''
    f = CellMaker((0,0), clen=60)
    f.background('f', { 'bg': 'F00' })
    f.foreground(
      'f', { 'fill': 'FF0', 'shape':'line', 'facing':'north', 'size': 'small' }
    )
    sqring = f.evalSeeker(f.bft[1], f.bft[0])
    self.assertEqual(sqring.this.name, 'sqring')
    self.writer.plotSqring(sqring.this.data)
    f.prettyPrint()
    '''
    line = sqring.this.lineFill('all')
    print(line)
    '''
'''
the
end
'''
