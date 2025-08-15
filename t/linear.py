import unittest
import pprint
from block import TmpFile, Make
from model import SvgLinear
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_a(self):
    ''' write preview of flatten as a wireframe
    '''
    svglin = SvgLinear(clen=54)
    block  = Make(clen=54)
    #pp.pprint(config.cells)
    block.walk(config.positions, config.cells)
    block.hydrateGrid()
    svglin.explode(block)
    svglin.render(model='minkscape')

  def test_3(self):
    ''' generate config for meander
    svg = LinearSvg()
    blocksize = (3, 1)
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    self.f.run(block1)
    meander_conf = svg.wireframe(self.f.done, writeconf=True)
    self.assertEqual(len(meander_conf), 207)
    '''

  def test_4(self):
    ''' Layout.Grid transforms a block into blocks according to position
    expectedx = [5, 50, 5, 50, 5, 50, 5, 50, 5, 50, 5, 50]
    expectedy = [5, 5, 20, 20, 35, 35, 50, 50, 65, 65, 80, 80]
    grid      = Grid(scale=1, gridsize=90)
    svg       = LinearSvg(scale=1, gridsize=90)
    blocksize = (3, 1)
    block1    = self.gm.make(blocksize, config.positions, config.cells)
    blocks    = grid.walk(blocksize, block1)
    for i, block in enumerate(blocks):
      x, y = block[0].shape.bounds[:2]
      self.assertEqual(expectedx[i], x)
      self.assertEqual(expectedy[i], y)
    '''

  def test_5(self):
    ''' write minkscape as 2d SVG
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
    svgfile = svg.make('linearsvg_5', todo, meander_conf=conf['meander'])
    svg.write(svgfile)
    '''
'''
the
end
'''
