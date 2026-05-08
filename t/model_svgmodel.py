import unittest
import pprint
from cell.minkscape import *
from model import Build

# TODO
'''
  sending unknown model names causes new ones to be created :/
  need filenames for visual test
'''
class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def test_a(self, LINE=True, BUILD=True, MODEL=None):
    ''' build SVG
    '''
    clen   = 20
    scale  = 1.0
    #block  = Make(clen=clen, linear=LINE)
    #svglin = SvgModel(clen=clen, scale=scale)
    MODEL  = MODEL if MODEL else 'svgmodel_test_a'
    b      = Build()

    #block.walk(minkscape.positions, minkscape.cells)
    #block.hydrateGrid()
    if BUILD: b.build(MODEL, clen, scale, linear=LINE)
    else:     b.build(MODEL, clen, scale, linear=LINE, explode=True)

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
      (1.0, 28): (280, 280),
      (1.0, 26): (260, 260),
      (0.4, 25): (270, 675),  # 25 is odd and diamonds notice
      (0.5, 24): (264, 528),
      (1.0, 24): (264, 264),
      (1.0, 22): (264, 264),
      (0.4, 20): (272, 680),
      (0.5, 20): (270, 540),
      (1.0, 20): (280, 280),
      (1.0, 18): (270, 270)
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


  def test_f(self):
    ''' 2 layer

        visual test use gthumb
    TODO avoid dep by moving these test to model_svgmodel
    OR matplotlib
    '''
    bm = Make(90)
    svg = SvgModel(90)
    bm.walkTwo(minkscape.positions, minkscape.cells)
    bm.hydrateGrid()
    svg.build(bm)
    svg.render('blockmake_test_f')

  def test_h(self):
    ''' test exploder walks the grid
    '''
    a0      = LinearRing(((0,0), (0,9), (9,9), (9,0)))
    a1      = LinearRing(((4,4), (4,6), (6,6), (6,4)))
    a       = Polygon(a0, holes=[a1])
    b       = Polygon(((9,0), (9,9), (18,5)))
    c       = Polygon(((0,15), (9,18), (9,9)))
    d       = Polygon(((9,9), (9,18), (18,18), (18,9)))
    block   = [a, b, c, d]
    CLEN    = 9
    b0, b1  = (2, 2)  # blocksize
    gsize   = 3
    edge    = gsize * CLEN

    svglin  = SvgModel(CLEN)
    model   = svglin.walk(block, gsize, b0, b1, CLEN, edge)
    mp      = MultiPolygon(model)
    if self.VERBOSE: self.writer.plot(mp, self.id())
  
'''
the 
end
'''
