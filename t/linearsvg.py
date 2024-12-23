import unittest
import pprint
from outfile import LinearSvg
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def test_1(self):
    ''' write minkscape as 2d SVG
    '''
    svg = LinearSvg(scale=2)
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    svg.make()
    svg.write('tmp/linearsvg_1.svg')

  def test_2(self):
    ''' write preview of flatten as a wireframe
    '''
    svg = LinearSvg(scale=2)
    blocksize = (3, 1)
    svg.gridwalk(blocksize, config.positions, config.cells)
    svg.wireframe()
    svg.write('tmp/linearsvg_2.svg')
