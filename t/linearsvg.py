import unittest
import pprint
from block.tmpfile import TmpFile
from outfile import LinearSvg, Grid
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_1(self):
    ''' write minkscape as 2d SVG
    '''
    grid      = Grid(scale=2, gridsize=90)
    svg       = LinearSvg(scale=2, gridsize=90)
    blocksize = (3, 1)
    conf      = self.tf.modelConf('minkscape')
    blocks    = grid.walk(blocksize, conf['cells'])
    svg.make(blocks, meander_conf=conf['meander'])
    svg.write('tmp/linearsvg_1.svg')

  def test_2(self):
    ''' write preview of flatten as a wireframe
    '''
    grid      = Grid(scale=2, gridsize=90)
    svg       = LinearSvg(scale=2)
    blocksize = (3, 1)
    conf      = self.tf.modelConf('minkscape')
    blocks    = grid.walk(blocksize, conf['cells'])
    svg.wireframe(blocks[0])
    svg.write('tmp/linearsvg_2.svg')

  def test_3(self):
    ''' write minkscape wireframe using conf/
    '''
    svg = LinearSvg()
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    cell_conf, block1 = svg.blockOne()
    meander_conf = svg.wireframe(block1, writeconf=True)
    self.assertEqual(len(cell_conf + meander_conf), 283)

'''
the
end
'''
