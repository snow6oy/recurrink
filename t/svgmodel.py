import unittest
import pprint
from cell.minkscape import *
from block import TmpFile, Make
from model import SvgModel
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_a(self, LINE=1.0, BUILD=True, MODEL=None):
    ''' prototype of build with SvgModel()
        PARAMS in caps should be set by argparse
    '''
    block  = Make(clen=45, linear=LINE)
    svglin = SvgModel(clen=45)
    MODEL  = MODEL if MODEL else 'svgmodel_test_a'

    block.walk(minkscape.positions, minkscape.cells)
    block.hydrateGrid(stroke_width=LINE)
    if BUILD: svglin.build(block)
    else:     svglin.explode(block)
    svglin.render(MODEL, line=LINE)

  def test_b(self): self.test_a(LINE=0,BUILD=False, MODEL='svgmodel_test_b')
  def test_c(self): self.test_a(LINE=0,BUILD=True,  MODEL='svgmodel_test_c')
  def test_d(self): self.test_a(LINE=True, BUILD=False, MODEL='svgmodel_test_d')

'''
the
end
'''
