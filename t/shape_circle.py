import unittest
import pprint
from cell.shape import Circle
from cell.minkscape import *
from cell import Build # Layer
from model.tester import SvgWriter

class Test(unittest.TestCase):
  VERBOSE = True
  pp      = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.cell   = minkscape.cells
    self.clen   = 18 # cell length
    self.circle = Circle() # 'c', cell_c)
    #self.layer  = Layer()
    self.build  = Build()
    self.writer = SvgWriter()

  def test_a(self):
    ''' circle
    '''
    self.assertEqual(self.circle.name, 'circle')

  def test_b(self):
    ''' large circle written as polygon
    '''
    geom         = self.cell['c']['geom']
    geom['name'] = 'circle'
    geom['size'] = 'large'
    x, y, stroke_width, clen = 3, 3, 0, self.clen
    points = self.build.points(x, y, stroke_width, self.clen)
    polygn = self.circle.paint(points, geom)
    self.assertEqual('Polygon', polygn.geom_type)
    if self.VERBOSE: self.writer.plot(polygn, self.id())

  def test_c(self, size='medium'):
    ''' linear circles
    '''
    points  = self.build.points(1, 1, 0, self.clen) # pos 1 1 
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
    points  = self.build.points(0, 0, 0, self.clen)
    geom    = self.cell['c']['geom']
    polyln  = self.circle.drawConcentric(points, geom)
    '''
    for g in polyln.geoms:
      print(g.geom_type)
    '''
    if self.VERBOSE: self.writer.plotLine(polyln, self.id())
 
  def test_g(self, size='medium', pos=tuple([0, 0])):
    '''
    circles need to adjust points according to size when drawn.
    examples:
    2558c8da8ed39d47f50c36b9a7ae1531 large fails while drawing first circle
    023a35ab5e6e3959253aba8294bc6b0a small draws single line in wrong cell
    dba0332ab181c8c6b93f5bad8ed5ad3a medium is ok
    '''
    expected = {
      'medium': {
          (0, 0): { 'e': (18, 9.0), 'w': (0, 9.0), 'ne': (18, 0), 'sw': (0, 18)
        }
      },
      'large': {
          (1, 0): { 'e': (39, 9), 'w': (15, 9), 'ne': (39, -3), 'sw': (15, 21)
        }
      },
      'small': {
          (1, 1): { 'e': (33, 27), 'w': (21, 27), 'ne': (33, 21), 'sw': (21, 33)
        }
      }
    }
    cl  = 18 # clen
    bc  = Build(pos, cl, linear=True)
    X,Y = pos # pos 1 0
    swd = 0  # stroke_width
    pts = bc.points(X, Y, swd, cl)
    '''
    test results
    '''
    adjusted = self.circle.adjustSize(size, pts)
    #self.pp.pprint(adjusted)
    rs = {
      'e' : tuple(adjusted[3]), # only these four get adjusted
      'w' : tuple(adjusted[5]),
      'ne': tuple(adjusted[6]),
      'sw': tuple(adjusted[9])
    }
    for x in expected[size][pos]:
      '''
      print(x)
      print(expected[size][pos][x]) 
      print(rs[x])
      print('^' * 80)
      '''
      self.assertEqual(rs[x], expected[size][pos][x]) 

  def test_h(self): self.test_g(size='large', pos=tuple([1, 0]))
  def test_i(self): self.test_g(size='small', pos=tuple([1, 1]))
'''
the
end
'''
