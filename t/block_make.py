import unittest
import pprint
from shapely.geometry import MultiPolygon, Polygon, LinearRing
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
    #self.pp.pprint(bm.cells[(0,0)])
    self.assertEqual(9.0, bm.cells[(0,0)][0].bounds[-1])

  def test_c(self):
    ''' cells made with Shapely have direction
    '''
    bm = Make(linear=True)
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('LineString', bm.cells[(0,0)][0].geom_type)

  def test_d(self):
    ''' test type
    '''
    bm    = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    cell0 = bm.cells[0,0][0]
    self.assertEqual('Polygon', cell0.geom_type)

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
        #print(f'{z=} {len(bm.cells[pos])=}')
        if z < len(bm.cells[pos]):
          cell   = bm.cells[pos][z]
          x, y, *zz = cell.bounds
          to_test.append(tuple([int(x), int(y)]))
    if self.VERBOSE: self.pp.pprint(to_test)
    self.assertEqual(len(expected), len(to_test))
    [self.assertEqual(e, to_test[i]) for i, e in enumerate(expected)]

  def test_f(self):
    ''' 2 layer

        visual test use gthumb
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
    expected    = [
      '#F00_00', '#F00_11', '#F00_12', '#F00_13', '#F00_24', '#F00_25'
    ]
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

  def test_h(self):
    ''' test exploder walks the grid
    '''
    a0      = LinearRing(((0,0), (0,9), (9,9), (9,0)))
    a1      = LinearRing(((4,4), (4,6), (6,6), (6,4)))
    a       = Polygon(a0, holes=[a1])
    b       = Polygon(((9,0), (9,9), (18,5)))
    c       = Polygon(((0,15), (9,18), (9,9)))
    d       = Polygon(((9,9), (9,18), (18,18), (18,9)))
    block   = [a, b, c, d]
    CLEN    = 9
    b0, b1  = (2, 2)  # blocksize
    gsize   = 3
    edge    = gsize * CLEN

    svglin  = SvgModel(CLEN)
    model   = svglin.walk(block, gsize, b0, b1, CLEN, edge)
    mp      = MultiPolygon(model)
    if self.VERBOSE: self.writer.plot(mp, self.id())

  
'''
the 
end
'''
