import unittest
import pprint
from shapely.geometry import Polygon, MultiLineString, LineString
from cell import Shape, Plotter, CellMaker, Meander
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.writer = Plotter()
    self.VERBOSE = True

  def test_a(self):
    ''' eflat cell f makes an irregular sqring flattened from a small line
    '''
    f = CellMaker((0,0), clen=60)
    f.background('f', { 'bg': 'F00' })
    f.foreground(
      'f', { 'fill': 'FF0', 'shape':'line', 'facing':'north', 'size': 'small' }
    )
    sqring = f.evalSeeker(f.bft[1], f.bft[0])
    self.assertEqual(sqring.this.name, 'irregular')
    if self.VERBOSE:
      f.prettyPrint()
      line = sqring.this.lineFill(clen=60, facing='all')
      self.writer.plotLine(line, self.id())

  def test_b(self):
    ''' from koto cell c
    # good [(9.0, 21.0), (7.0, 21.0), (7.0, 23.0), (9.0, 23.0), (9.0, 21.0)]
    '''
    outer = [(14.0, 29.0), (14.0, 16.0), (1.0, 16.0), (1.0, 29.0),(14.0, 29.0)]
    hole = [(9.0, 22.0), (7.0, 22.0), (7.0, 24.0), (9.0, 24.0), (9.0, 22.0)]
    p  = Polygon(outer, holes=[hole])
    self.writer.plotShape(p, self.id())
    m     = Meander(p)
             #m.matrix(15)
    line  = [[0, 16], [0, 17], [0, 18], [0, 19], [0, 20], [0, 21], [0, 22], [0, 23], [0, 24], [0, 25], [0, 26], [0, 27], [0, 28], [0, 29], [0, 29], [1, 29], [2, 29], [3, 29], [4, 29], [5, 29], [6, 29], [7, 29], [8, 29], [9, 29], [10, 29], [11, 29], [12, 29], [13, 29], [14, 29], [14, 28], [14, 27], [14, 26], [14, 25], [14, 24], [14, 23], [14, 22], [14, 21], [14, 20], [14, 19], [14, 18], [14, 17], [14, 16], [14, 16], [13, 16], [12, 16], [11, 16], [10, 16], [9, 16], [8, 16], [7, 16], [6, 16], [5, 16], [4, 16], [3, 16], [2, 16], [1, 16], [1, 17], [1, 18], [1, 19], [1, 20], [1, 21], [1, 22], [1, 23], [1, 24], [1, 25], [1, 26], [1, 27], [1, 28], [1, 28], [2, 28], [3, 28], [4, 28], [5, 28], [6, 28], [7, 28], [8, 28], [9, 28], [10, 28], [11, 28], [12, 28], [13, 28], [13, 27], [13, 26], [13, 25], [13, 24], [13, 23], [13, 22], [13, 21], [13, 20], [13, 19], [13, 18], [13, 17], [13, 16], [12, 16], [11, 16], [10, 16], [9, 16], [8, 16], [7, 16], [6, 16], [5, 16], [4, 16], [3, 16], [2, 16], [2, 17], [2, 18], [2, 19], [2, 20], [2, 21], [2, 22], [2, 23], [2, 24], [2, 25], [2, 26], [2, 27], [3, 27], [4, 27], [5, 27], [6, 27], [7, 27], [8, 27], [9, 27], [10, 27], [11, 27], [12, 27], [12, 26], [12, 25], [12, 24], [12, 23], [12, 22], [12, 21], [12, 20], [12, 19], [12, 18], [12, 17], [11, 17], [10, 17], [9, 17], [8, 17], [7, 17], [6, 17], [5, 17], [4, 17], [3, 17], [3, 18], [3, 19], [3, 20], [3, 21], [3, 22], [3, 23], [3, 24], [3, 25], [3, 26], [4, 26], [5, 26], [6, 26], [7, 26], [8, 26], [9, 26], [10, 26], [11, 26], [11, 25], [11, 24], [11, 23], [11, 22], [11, 21], [11, 20], [11, 19], [11, 18], [10, 18], [9, 18], [8, 18], [7, 18], [6, 18], [5, 18], [4, 18], [4, 19], [4, 20], [4, 21], [4, 22], [4, 23], [4, 24], [4, 25], [5, 25], [6, 25], [7, 25], [8, 25], [9, 25], [10, 25], [10, 24], [10, 23], [10, 22], [10, 21], [10, 20], [10, 19], [9, 19], [8, 19], [7, 19], [6, 19], [5, 19], [5, 20], [5, 21], [5, 22], [5, 23], [5, 24], [6, 24], [7, 24], [8, 24], [9, 24], [9, 23], [9, 22], [9, 21], [9, 20], [8, 20], [7, 20], [6, 20], [6, 21], [6, 22], [6, 23], [7, 23], [8, 23], [8, 22], [8, 21], [7, 21], [7, 22]]

    mls   = m.splitLines(line, Polygon(hole)) #small.interiors[0])
    self.writer.plotLine(mls, self.id())
    '''
    print(line)


    c  = Shape('c', {'shape': 'irregular','facing':'all'})
    if c.compute(p): # return True means the bad hole was silently fixed
      line  = b.this.lineFill(facing=b.facing)
      if self.VERBOSE: self.writer.plotLine(line, fn='t_sqring_c')
      self.assertEqual(36, len(list(line.coords)))
    else:
      self.assertFalse(True) # fail as bad hole went undetected
    '''

'''
the
end
'''
