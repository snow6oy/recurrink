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
    block1  = gm.make(blocksz, config.positions, config.cells)
    self.assertEqual(block1[0].pencolor, '00F')

  def test_2(self):
    ''' cell names are kept in block1
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeCells(blocksz, config.positions, config.cells)
    self.assertEqual(block1[pos].names[-1], 'c')

  def test_3(self):
    ''' cells made with Shapely
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    pos     = (0,0)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    #self.assertEqual(block1[pos].names[-1], 'c')

  def test_4(self):
    ''' disable this once print works
    '''
    [print(f"cn {e[0]} layer {e[1]} x {e[2]} y {e[3]} w {e[4]} y {e[5]}") 
      for e in self.expected]

  def test_5(self):
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    to_test = dict()
    for pos, cell in block1.items():
      for i, layer in enumerate(cell.bft):
        svg_vals = list(layer.shape.svg().values())
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
    large   = gm.discoverDanglers(block1)
    self.assertEqual('MultiPolygon', large[0].geom_type)
    '''
    large   = gm.largeShapes(block1)
    self.assertFalse(len(block1[(0,0)].bft))
    self.assertTrue(len(block1[(1,0)].bft))   # cell b is a large line
    self.assertFalse(len(block1[(2,0)].bft))
    '''

  def test_7(self):
    ''' extract overlap
    '''
    gm      = GeoMaker()
    blocksz = (3,1)
    block1  = gm.makeShapelyCells(blocksz, config.positions, config.cells)
    large   = gm.discoverDanglers(block1)
    found   = gm.findNeighbours(block1, large)
    p0, p1  = list(found.keys())
    self.assertEqual((0, 0), p0)
    self.assertEqual((2, 0), p1)



'''
the 
end
'''
