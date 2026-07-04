import unittest
import pprint
#from cell.minkscape import *
from shapely import Polygon
from block.build import Build, Make
from model.svg import SvgModel # for visual tests
from model.data import ModelData
from model.tester import SvgWriter

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.VERBOSE = False
    self.writer  = SvgWriter()

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

  def test_e(self):
    ''' 2558c8da8ed39d47f50c36b9a7ae1531 must be cloned beforehand
        has a large circle that fails to draw first circle
    '''
    bb       = Build()
    md       = ModelData()
    svg      = SvgModel(clen=24, scale=1.0)
    pos      = md.blocks(9) # arpeggio = mid 9
    pens     = [None, 'uniball', 'copicsketch', 'copic', 'stabilo68']
    model    = 'arpeggio'
    block, _ = bb.build(
      model, 24, 1.0, positions=pos, pens=pens, linear=True
    )
    svg.build(block)
    svg.render('bb_test_e', True)

  def test_f(self):

    mk = Make(clen=36, linear=True)
    positions = { 
      (0, 0): ('a', None),
      (1, 0): ('a', None),
      (2, 0): ('a', None)
    }
    cells     = {'a': 
      { 'color': 
        {'background': '#ff6600', 'fill': '#483737', 'opacity': 1.0},
        'geom': 
        {'facing': 'C', 'name': 'circle', 'size': 'large', 'top': False}
      }
    }
    mk.walkThree(positions, cells)
    #self.pp.pprint(mk.cells[(0,0)][1]) # circle is in layer 1
    polygon = Polygon(mk.cells[(0, 0)][1])
    if self.VERBOSE: self.writer.plot(polygon, self.id())

'''
the 
end
'''
