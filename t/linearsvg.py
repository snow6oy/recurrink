import unittest
import pprint
from tmpfile import TmpFile
from outfile import LinearSvg
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_1(self):
    ''' write minkscape as 2d SVG
    '''
    svg = LinearSvg(scale=2)
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    mc = self.tf.modelConf('minkscape', 'meander')
    svg.make(meander_conf=mc)
    svg.write('tmp/linearsvg_1.svg')

  def test_2(self):
    ''' write preview of flatten as a wireframe
    '''
    svg = LinearSvg(scale=2)
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    svg.wireframe()
    svg.write('tmp/linearsvg_2.svg')

  def test_3(self):
    ''' write minkscape wireframe using conf/
    '''
    svg = LinearSvg(scale=2)
    cells = self.tf.modelConf('minkscape', 'cells')
    svg.wireframe(cells=cells)
    svg.write('tmp/linearsvg_3.svg')

  def test_4(self):
    pass
    '''
    svgfile = f'tmp/{model}_mm.svg'
    mc      = tf.modelConf(model, 'meander')
    svg.make(meander_conf=mc)
    '''

