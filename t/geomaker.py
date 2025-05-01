import unittest
import pprint
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
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

  def test_1(self):
    gm = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(block1[(0,0)].bft[0].fill, 'F00')

  def test_2(self):
    ''' cell names are kept in block1
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(block1[pos].bft[2].label, 'c')

  def test_3(self):
    ''' cells made with Shapely
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    self.assertEqual(60, block1[pos].clen)

  def test_4(self): pass

  def test_5(self):
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    to_test = dict()
    for pos, cell in block1.items():
      for i, layer in enumerate(cell.bft):
        svg_vals = list(layer.this.svg().values())
        label_i  = layer.label + str(i)
        to_test[label_i] = svg_vals[1:]
    #pp.pprint(to_test)
    self.assertEqual(len(self.expected), len(to_test))
    for e in self.expected:
      self.assertEqual(self.expected[e], to_test[e])

  def test_6(self):
    ''' filter block1 so that only cells with large shapes remain
    '''
    gm = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    large   = gm.largeShapes(block1)
    self.assertEqual('MultiPolygon', large[0].geom_type)

  def test_7(self):
    ''' extract overlap
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    large   = gm.largeShapes(block1)
    found   = gm.findNeighbours(block1, large)
    p0, p1  = list(found.keys())
    self.assertEqual((0, 0), p0)
    self.assertEqual((2, 0), p1)

  def test_8(self):
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
'''
the 
end
'''
