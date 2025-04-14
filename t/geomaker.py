import unittest
import pprint
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

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
'''
the 
end
'''
