import unittest
import pprint
from cell.minkscape import *
from block import TmpFile, Make
from model import SvgModel
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf  = TmpFile()

  def test_a(self, LINE=True, BUILD=True, MODEL=None):
    ''' prototype of build with SvgModel()
        PARAMS in caps should be set by argparse
    '''
    clen   = 20
    scale  = 1.0
    block  = Make(clen=clen, linear=LINE)
    svglin = SvgModel(clen=clen, scale=scale)
    MODEL  = MODEL if MODEL else 'svgmodel_test_a'

    block.walk(minkscape.positions, minkscape.cells)
    block.hydrateGrid()
    if BUILD: svglin.build(block)
    else:     svglin.explode(block)
    svglin.render(MODEL, line=LINE)

  def test_b(self): self.test_a(LINE=False,BUILD=False, MODEL='svgmodel_test_b')
  def test_c(self): self.test_a(LINE=False,BUILD=True,  MODEL='svgmodel_test_c')
  def test_d(self): self.test_a(LINE=True, BUILD=False, MODEL='svgmodel_test_d')

  def test_e(self):
    ''' generate clen and scale combinations
    '''
    expected = {
      (0.4, 40): (272, 680),
      (0.5, 40): (280, 560),
      (1.0, 40): (280, 280),
      (1.0, 38): (266, 266),
      (0.5, 36): (270, 540),
      (1.0, 36): (288, 288),
      (0.4, 35): (266, 665),  # odd
      (1.0, 34): (272, 272),
      (0.5, 32): (272, 544),
      (1.0, 32): (256, 256),
      (0.4, 30): (264, 660),
      (1.0, 30): (270, 270),
      (0.5, 28): (266, 532),
      (1.0, 28): (280, 280)
      (1.0, 26): (260, 260),
      (0.4, 25): (270, 675),  # 25 is odd and diamonds notice
      (0.5, 24): (264, 528),
      (1.0, 24): (264, 264),
      (1.0, 22): (264, 264),
      (0.4, 20): (272, 680),
      (0.5, 20): (270, 540),
      (1.0, 20): (280, 280),
      (1.0, 18): (270, 270),
    }
    for clen in range(18, 41):
      for s in [0.4, 0.5, 1.0]:
        scaled =  clen * s
        if scaled % 2: continue
        #if scaled < 7 or scaled >= 40: continue
        svg = SvgModel(clen=clen, scale=s)
        '''
        print(f'{(s, svg.clen)}: {(svg.gridsz[0], svg.viewbx[0])}')
        '''
        gridsz, viewbx = expected[(s, svg.clen)]
        self.assertEqual(gridsz, svg.gridsz[0])
        self.assertEqual(viewbx, svg.viewbx[0])

'''
the
end
'''
