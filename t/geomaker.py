import unittest
import pprint
from shapely.geometry import MultiPolygon, Polygon
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.VERBOSE = False
    # cn layer x y w h
    self.expected = {
      'a0': [0, 0, 60, 60], 
      'b0': [60, 0, 60, 60], 
      'c0': [120, 0, 60, 60], 
      'a1': [0, 0, 60, 60], 
      'b1': [80, 0, 20, 60], 
      'c1': [140, 20, 20, 20], 
      'c2': [20, 20, 20, 20], 
      'd2': [40, 20, 100, 20]
    }

  def test_a(self):
    gm = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(block1[(0,0)].bft[0].fill, 'F00')

  def test_b(self):
    ''' cell names are kept in block1
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(block1[pos].bft[2].label, 'c')

  def test_c(self):
    ''' cells made with Shapely
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(60, block1[pos].clen)

  def test_d(self): pass

  def test_e(self):
    ''' svg coords for each minkscape cell
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    to_test = dict()
    for pos, cell in block1.items():
      for i, layer in enumerate(cell.bft):
        svg_vals = list(layer.this.svg().values())
        label_i  = layer.label + str(i)
        to_test[label_i] = svg_vals
    if self.VERBOSE: pp.pprint(to_test)
    self.assertEqual(len(self.expected), len(to_test))
    for e in self.expected:
      self.assertEqual(self.expected[e], to_test[e])

  def test_f(self):
    ''' filter block1 so that only cells with large shapes remain
    '''
    cells =  config.cells
    cells['a']['size'] = 'large'
    gm = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    large   = gm.largeShapes(block1)
    self.assertEqual('Polygon', large[0].geom_type)
    self.assertEqual('Polygon', large[1].geom_type)

  def test_g(self):
    ''' extract overlap
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    large   = gm.largeShapes(block1)
    found   = gm.findNeighbours(block1, large)
    self.assertEqual(2, len(found))
    self.assertTrue((0, 0) in list(found.keys()))
    self.assertTrue((2, 0) in list(found.keys()))

  def test_h(self):
    ''' pad all shapes in block1
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    a0      = block1[(0,0)].bft[0].this.data.bounds
    padme   = gm.padBlock(block1)
    a0_pad  = block1[(0,0)].bft[0].this.data.bounds
    self.assertEqual(60, a0[-1])
    self.assertEqual(59, a0_pad[-1])

  def test_i(self):
    ''' convert a cell with a multipolygon into two new shapes
    '''
    p1      = Polygon(((0,0), (0,30), (60,30), (60,0), (0,0)))
    p2      = Polygon(((0,30), (0,60), (60,60), (60,30), (0,30)))
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    cell    = block1[0,0]
    cell.bft[1].this.name = 'multipolygon'
    cell.bft[1].this.data = MultiPolygon([p1, p2])
    cell    = gm.splitByCell(cell)

    for layer in cell.bft[2:]: # check last two items are p1 and p2
      self.assertEqual('line', layer.this.name)
     
  def test_j(self):
    ''' split multi geoms and eliminate all MultiPolygons across block1
    '''
    p1           = Polygon(((0,0), (0,30), (60,30), (60,0), (0,0)))
    p2           = Polygon(((0,30), (0,60), (60,60), (60,30), (0,30)))
    p3           = Polygon(((20, 20), (20, 40), (30, 40), (30, 20), (20, 20)))
    p4           = Polygon(((30, 20), (30, 40), (40, 40), (40, 20), (30, 20)))
    gm           = GeoMaker()
    blocksz      = (3,1)
    block1       = gm.makeShapelyCells(blocksz, config.positions, config.cells)
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
the 
end
'''
