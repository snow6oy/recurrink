import unittest
import pprint
from shapely.geometry import MultiPolygon, Polygon
from block import Make
from cell.minkscape import *
from model import SvgModel

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)
  def setUp(self):
    self.VERBOSE = False

  def test_a(self):
    ''' make cell and check style
    '''
    bm = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('#F00', bm.style.fill[(0,0)][0])

  def test_b(self):
    ''' cell geoms are kept in block1
    '''
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual(9.0, bm.cells[(0,0)].geoms[0].bounds[-1])

  def test_c(self):
    ''' cells made with Shapely have direction
    '''
    bm = Make(linear=True)
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('MultiLineString', bm.cells[(0,0)].geom_type)

  def test_d(self):
    ''' test type
    '''
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    cell    = bm.cells[0,0]
    self.assertEqual('MultiPolygon', cell.geom_type)

  def test_e(self):
    ''' svg coords for each minkscape cell
    '''
    expected = [
      (0, 0), (9, 0), (18, 0), (0, 0), (12, 0), (21, 3), (3, 3), (6, 3)
    ]
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    to_test = list()
    for z in range(3):
      for pos in bm.cells:
        polygn = bm.polygon(pos, z)
        if polygn:
          x, y, *zz = polygn.bounds
          to_test.append(tuple([int(x), int(y)]))
    if self.VERBOSE: pp.pprint(to_test)
    self.assertEqual(len(expected), len(to_test))
    [self.assertEqual(e, to_test[i]) for i, e in enumerate(expected)]

  def test_f(self):
    ''' 2 layer
    '''
    bm = Make(90)
    svg = SvgModel(90)
    bm.walkTwo(minkscape.positions, minkscape.cells)
    bm.hydrateGrid()
    svg.build(bm)
    svg.render('blockmake_test_f')

  def test_g(self):
    ''' pens that appear in multiple styles
        must still have unique names
    '''
    expected    = ['#F00_00', '#F00_11', '#F00_12', '#F00_13', '#F00_24', '#F00_25']
    same_colour = minkscape.cells      # should be deep copy?
    opacities   = [0.1, 0.2, 0.3, 0.4] # different styles to make test case
    penams      = list()
    for label, cell in same_colour.items():
      cell['color']['fill'] = '#F00'   # same pen to force test
      cell['color']['opacity'] = opacities.pop()
    bm = Make(linear=True)
    bm.walk(minkscape.positions, same_colour)
    bm.hydrateGrid()
    for layer in bm.grid:
      for style in layer:
        penams.append(layer[style]['penam'] )
    self.assertEqual(penams, expected)

  
'''
the 
end
'''
