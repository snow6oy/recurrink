import unittest
import pprint
from cell.minkscape import *
from block import TmpFile, Make
from model import SvgLinear
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_a(self, LINE=True, BUILD=True, MODEL=None):
    ''' prototype of build with SvgLinear()
        PARAMS in caps should be set by argparse
    '''
    block  = Make(clen=90)
    svglin = SvgLinear(clen=90)
    MODEL  = MODEL if MODEL else 'linear_test_a'

    block.walk(minkscape.positions, minkscape.cells)
    if LINE: block.meander(padding=False)
    block.hydrateGrid(line=LINE)
    if BUILD: svglin.build(block)
    else:     svglin.explode(block)
    svglin.render(MODEL, line=LINE)

  def test_b(self): self.test_a(LINE=False, BUILD=False, MODEL='linear_test_b')
  def test_c(self): self.test_a(LINE=False, BUILD=True, MODEL='linear_test_c')
  def test_d(self): self.test_a(LINE=True, BUILD=False, MODEL='linear_test_d')

'''
the
end
'''
