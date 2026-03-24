import unittest
import pprint
import os.path
from block import BlockData
from cell.init import Geometry, Palette

class Test(unittest.TestCase):
  ''' use cases

      geometry.generateOne(axis, top, facing)
      geometry.generateFacingCentre(top)
      geometry.generateFacingAny(top)
      palette.generateOne(colors)
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.g       = Geometry()
    self.p       = Palette()
    self.VERBOSE = True

  def test_a(self):
    ''' Generate Any direction
    '''
    geom = self.g.generateFacingAny()  
    items = list(geom.keys())
    self.assertEqual(len(items), 4)

  def test_b(self):
    ''' cells must face all directions for allocation pool to generate output
    '''
    geom = self.g.generateFacingCentre()
    self.assertEqual(geom['facing'], 'C')

  def test_c(self):
    ''' after compass pair is applied 
        cells b and d should be symmetrical on east-west axis
    '''
    pair = ('b', 'd')  # soleares compass, just for context
    cell_b = self.g.generateOne(axis='E', top=False, facing=None)
    b_facing = cell_b['facing']
    self.assertTrue(b_facing in ['N', 'S'])
    cell_d = self.g.generateOne(axis='E', top=False, facing=b_facing)
    d_facing = cell_d['facing'] 
    self.assertTrue(b_facing != d_facing)

  def test_d(self):
    ''' Generate One randomly generate cell colours
    '''
    ver    = 1
    bd     = BlockData()
    colors = bd.colors(ver)
    #self.pp.pprint(colors)
    cell_z = self.p.generateOne(colors)
    #self.pp.pprint(cell_z)
    found = [c for c in colors if c[0] == cell_z['fill']]
    self.assertTrue(len(found))
'''
the
end
''' 
