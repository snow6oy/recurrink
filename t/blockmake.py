import unittest
import pprint
from shapely.geometry import MultiPolygon, Polygon
from block import Make
from cell.minkscape import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

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
    bm      = Make()
    bm.walk(minkscape.positions, minkscape.cells)
    self.assertEqual('spiral', bm.guide[(0,0)][1][0])

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
    ''' filter block1 so that only cells with large shapes remain
    cells =  minkscape.cells
    cells['a']['size'] = 'large'
    bm.walk(minkscape.positions, minkscape.cells)
    large   = gm.largeShapes(block1)
    self.assertEqual('Polygon', large[0].geom_type)
    self.assertEqual('Polygon', large[1].geom_type)
    '''
    pass

  def test_g(self):
    ''' extract overlap
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, minkscape.positions, minkscape.cells)
    large   = gm.largeShapes(block1)
    found   = gm.findNeighbours(block1, large)
    self.assertEqual(2, len(found))
    self.assertTrue((0, 0) in list(found.keys()))
    self.assertTrue((2, 0) in list(found.keys()))
    '''
    pass

  def test_h(self):
    ''' pad all shapes in block1
    a0      = block1[(0,0)].bft[0].this.data.bounds
    padme   = gm.padBlock(block1)
    a0_pad  = block1[(0,0)].bft[0].this.data.bounds
    self.assertEqual(60, a0[-1])
    self.assertEqual(59, a0_pad[-1])
    '''

  def test_i(self):
    ''' convert a cell with a multipolygon into two new shapes
    p1      = Polygon(((0,0), (0,30), (60,30), (60,0), (0,0)))
    p2      = Polygon(((0,30), (0,60), (60,60), (60,30), (0,30)))
    cell.bft[1].this.data = MultiPolygon([p1, p2])
    cell    = gm.splitByCell(cell)
    for layer in cell.bft[2:]: # check last two items are p1 and p2
      self.assertEqual('line', layer.this.name)
    '''
     
  def test_j(self):
    ''' split multi geoms and eliminate all MultiPolygons across block1
    p1           = Polygon(((0,0), (0,30), (60,30), (60,0), (0,0)))
    p2           = Polygon(((0,30), (0,60), (60,60), (60,30), (0,30)))
    p3           = Polygon(((20, 20), (20, 40), (30, 40), (30, 20), (20, 20)))
    p4           = Polygon(((30, 20), (30, 40), (40, 40), (40, 20), (30, 20)))
    gm           = GeoMaker()
    blocksz      = (3,1)
    block1       = gm.makeShapelyCells(blocksz, minkscape.positions, minkscape.cells)
    a1           = block1[0,0].bft[1]
    a1.this.name = 'multipolygon'
    a1.this.data = MultiPolygon([p1, p2])
    c1           = block1[2,0].bft[1]
    c1.this.name = 'multipolygon'
    c1.this.data = MultiPolygon([p3, p4])
    block1       = gm.splitMultigeoms(block1)

    for pos in block1:
      for layer in block1[pos].bft:
        self.assertNotEqual('MultiPolygon', layer.this.data.geom_type)
    '''
     
'''
the 
end
'''
