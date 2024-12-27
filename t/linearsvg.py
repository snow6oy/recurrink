import unittest
import pprint
from tmpfile import TmpFile
from outfile import LinearSvg
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def test_1(self):
    ''' write minkscape as 2d SVG
    '''
    tf  = TmpFile()
    svg = LinearSvg(scale=2)
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    mc = tf.meanderConf('minkscape')
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
