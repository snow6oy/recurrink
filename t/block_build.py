import unittest
import pprint
from cell.minkscape import *
from block import Build
from model.svg import SvgModel # for visual tests

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def test_a(self, LINE=True, BUILD=True, svgfile='bb_test_a'):
    ''' obtain a Make object and convert it to SVG
    '''
    bb        = Build()
    clen      = 20
    scale     = 1.0
    svg       = SvgModel(clen, scale)
    model     = 'minkscape' 
    #svgfile   = svgfile if svgfile else 'bb_test_a'
    pens      = [None, 'uniball']
    positions = {
      (0, 0): ('a', 'c'), (1, 0): ('b', 'd'), (2, 0): ('c', None)
    }

    if BUILD: 
      block, _ = bb.build( # ignore pal 
        model, clen, scale, positions=positions, pens=pens, linear=LINE
      )
      svg.build(block)
    else:     
      block, _ = bb.build(
        model, clen, scale, positions=positions, pens=pens, linear=LINE,
        explode=True
      )
      svg.explode(block)

    svg.render(svgfile, LINE)

  def test_b(self): self.test_a(LINE=False, BUILD=False, svgfile='bb_test_b')
  def test_c(self): self.test_a(LINE=False, BUILD=True, svgfile='bb_test_c')
  def test_d(self): self.test_a(LINE=True, BUILD=False, svgfile='bb_test_d')

'''
the 
end
'''
