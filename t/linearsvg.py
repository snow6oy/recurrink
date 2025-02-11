import unittest
import pprint
from block import TmpFile, Flatten, GeoMaker
#from block.make import GeoMaker
from model import LinearSvg, Grid
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()
    self.f   = Flatten()
    self.gm  = GeoMaker()

  def test_1(self):
    ''' load minkscape and check block has correct number of shapes
    '''
    blocksize = (3, 1)
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    self.assertEqual(len(block1), 8)

  def test_2(self):
    ''' write preview of flatten as a wireframe
    '''
    svg       = LinearSvg(scale=2)
    blocksize = (3, 1)
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    self.f.run(block1)
    svg.wireframe(self.f.done)
    svg.write('tmp/linearsvg_2.svg')

  def test_3(self):
    ''' generate config for meander
    '''
    svg = LinearSvg()
    blocksize = (3, 1)
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    self.f.run(block1)
    meander_conf = svg.wireframe(self.f.done, writeconf=True)
    self.assertEqual(len(meander_conf), 207)

  def test_4(self):
    ''' write minkscape as 2d SVG
    '''
    todo      = []
    grid      = Grid(scale=1, gridsize=90)
    svg       = LinearSvg(scale=1, gridsize=90)
    blocksize = (3, 1)
    conf      = self.tf.modelConf('minkscape')
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    blocks    = grid.walk(blocksize, block1)
    for b in blocks:
      f = Flatten()
      todo.append(f.run(b))
    svgfile = svg.make('linearsvg_1', todo, meander_conf=conf['meander'])
    svg.write(svgfile)
'''
the
end
'''
