import unittest
import pprint
from block import TmpFile, Flatten
from model.svg import LinearSvg # explicit import due to circular dependency
from model import Grid
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()
    self.f   = Flatten()

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
    self.f.run(blocks[0])
    svg.wireframe(self.f.done)
    svg.write('tmp/linearsvg_2.svg')

  def test_3(self):
    ''' write minkscape wireframe using conf/
    '''
    svg = LinearSvg()
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    cell_conf, block1 = svg.blockOne()
    self.f.run(block1)
    meander_conf = svg.wireframe(self.f.done, writeconf=True)
    self.assertEqual(len(cell_conf + meander_conf), 283)

  def test_4(self):
    ''' write preview of flatten as a wireframe
        1. obtain cells from tmp
        2. flatten cells and send flatten object 
    '''
    grid      = Grid(scale=2, gridsize=90)
    svg       = LinearSvg(scale=2)
    blocksize = (3, 1)
    cells     = self.tf.modelConf('minkscape', 'cells')
    '''
    pp.pprint(config.cells)
    '''
    blocks    = grid.walk(blocksize, config.cells)
    pp.pprint(blocks)
    '''
    svg.wireframe(blocks[0])
    svg.write('tmp/linearsvg_2.svg')
    '''

'''
the
end
'''
