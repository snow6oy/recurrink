import unittest
import pprint
from shapely.geometry import Polygon
from cell import Meander, Plotter
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):
  def setUp(self):
    self.writer  = Plotter()
    self.VERBOSE = False

  def test_j(self):
    ''' check each guideline by comparing grid order
    '''
    expect = [
      ( 4,  5,  1,  4, 15,  1),
      ( 4, 15,  1,  4, 15,  1),
      ( 4, 15,  1,  4,  5,  1),
      ( 4, 15,  1, 14,  3, -1),
      ( 4,  5,  1, 14,  3, -1),
      (14,  3, -1, 14,  3, -1),
      (14,  3, -1,  4,  5,  1),
      (14, 15,  1,  4, 15,  1),
      ( 4, 15,  1, 14, 15,  1),
      (14, 15,  1, 14,  3, -1),
      (14,  3, -1, 14, 15,  1),
      (14,  3, -1,  4, 15,  1) 
    ]
    d       = ('NL','NE','EB','SE','SL','SW','WB','NR','ET','SR','WT')
    r       = Meander(Polygon([(3, 3), (3, 15), (15, 15), (15, 3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme, direction=d)
    for i, g in enumerate(list(guides.geoms)):
      grid_ord = r.orderGrid(g)
      self.assertEqual(expect[i], grid_ord)

  def test_a(self): 
    ''' guidelines for East with plot of before and after padding
    '''
    r       = Meander(Polygon([(3, 3), (3, 15), (15, 15), (15, 3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme, ('EB', 'ET'))
    if self.VERBOSE: self.writer.plot(r.shape, padme, 't_meander_a')
    # [print(list(g.coords)) for g in list(guides.geoms)]
    g = list(guides.geoms)[0]
    self.assertEqual(g.coords[0], (4.0, 4.0))

  def test_b(self): 
    ''' Rectangle with plot of stripes
    '''
    expect  = [(4,4), (14,14)]
    r       = Meander(Polygon([(3, 3), (3, 15), (15, 15), (15, 3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme, ('EB', 'ET'))
    pnts, _ = r.collectPoints(padme, guides) # ignore err
    stripes = r.makeStripes(pnts)
    first   = list(stripes.coords)[0]
    last    = list(stripes.coords)[-1]
    if self.VERBOSE: self.writer.plotLine(stripes, 't_meander_b')
    self.assertEqual(first, expect[0])
    self.assertEqual(last,  expect[1])

  def test_c(self):
    ''' Gnomon
    '''
    g       = Meander(Polygon([(3,3), (3,15), (15,15), (15,11), (7,11), (7,3)]))
    padme   = g.pad()
    guides  = g.guidelines(padme, ('WB', 'NW', 'NR'))  # (270, 315, 360))
    pnts, _ = g.collectPoints(padme, guides)
    stripes = g.makeStripes(pnts)
    if self.VERBOSE: self.writer.plotLine(stripes, 't_meander_c')
    self.assertEqual((6,4), list(stripes.coords)[0])
    self.assertEqual((14,14), list(stripes.coords)[-1])

  def test_d(self):
    ''' two Gnomons make a Polygon with a whole
    '''
    g      = Meander(Polygon([(3,3),(3,15),(7,15),(7,7),(15,7),(15,3)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad, ('ET', 'NE', 'NR'))
    p1, _  = g.collectPoints(gpad, guides)
    gg     = Meander(Polygon([(11,7),(11,11),(7,11),(7,15),(15,15),(15,7)]))
    ggpad  = gg.pad()
    guides = gg.guidelines(ggpad, ('NL', 'NE', 'EB'))
    p2, _  = g.collectPoints(ggpad, guides)
    stripe = g.joinStripes(p1, p2)
    if self.VERBOSE: self.writer.plotLine(stripe, 't_meander_d')
    xy     = list(stripe.coords)
    self.assertEqual((4,14), xy[0])
    self.assertEqual((8,12), xy[-1])

  def test_e(self):
    ''' one Gnomon plus Rectangle makes a Parabola
    '''
    g      = Meander(Polygon([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad, ('WB', 'SW', 'SL')) 
    p1, _  = g.collectPoints(gpad, guides)
    r      = Meander(Polygon([(0,0),(0,12),(6,12),(6,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad, ('NR', 'NL'))
    p2, _  = r.collectPoints(rpad, rguide)
    stripe = r.joinStripes(p1, p2)
    if self.VERBOSE: self.writer.plotLine(stripe, 't_meander_e')
    xy     = list(stripe.coords)
    self.assertEqual((17,1), xy[0])
    self.assertEqual((5,1), xy[-1])

  def test_f(self):
    ''' western Parabola
    '''
    g      = Meander(Polygon([(0,0),(0,18),(18,18),(18,12),(6,12),(6,0)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad, ('SR', 'SE', 'EB')) #450,135,90))
    p1, _  = g.collectPoints(gpad, guides)
    r      = Meander(Polygon([(6,0),(6,6),(18,6),(18,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad, ('WT', 'WB')) #  direction=(496,270))
    p2, _  = r.collectPoints(rpad, rguide)
    stripe = r.joinStripes(p1, p2)
    if self.VERBOSE: self.writer.plotLine(stripe, 't_meander_f')
    xy     = list(stripe.coords)
    self.assertEqual((17,17), xy[0])
    self.assertEqual((17,5), xy[-1])

  def test_g(self):
    ''' eastern Parabola
    '''
    g      = Meander(Polygon([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad, ('SL', 'SW', 'WB'))  #direction=(180,225,270))
    p1, _  = g.collectPoints(gpad, guides)
    r      = Meander(Polygon([(0,0),(0,6),(12,6),(12,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad, ('SL', 'SR')) # direction=(180,450))     # 495,270))
    p2, _  = r.collectPoints(rpad, rguide)
    stripe = r.joinStripes(p1, p2)
    if self.VERBOSE: self.writer.plotLine(stripe, 't_meander_g')
    xy     = list(stripe.coords)
    self.assertEqual((1,17), xy[0])
    self.assertEqual((1,5), xy[-1])

  def test_h(self):
    ''' one Gnomon plus Rectangle makes a Parabola
        can join even number of stripes
    '''
    g      = Meander(Polygon([(0,8),(0,13),(13,13),(13,0),(8,0),(8,8)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad, ('SL', 'SW', 'WB')) #  direction=(180,225,270))
    p1, _  = g.collectPoints(gpad, guides)
    r      = Meander(Polygon([(0,0),(0,8),(4,8),(4,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad, ('NR', 'NL')) # direction=(360,0))
    p2, _  = r.collectPoints(rpad, rguide)
    stripe = r.joinStripes(p1, p2)
    if self.VERBOSE: self.writer.plotLine(stripe, 't_meander_h')
    xy     = list(stripe.coords)
    self.assertEqual((1,12), xy[0])
    self.assertEqual((3,1), xy[-1])

  def test_i(self):
    ''' can NOT draw a north meander as a U-shape
         NW NE
        W     E
        it draws criss-cross because W and E are on the same axis
    '''
    m     = Meander(Polygon([(1,1),(1,13),(13,13),(13,1),(9,1),(9,9),(5,9),(5,1)]))
    padme = m.pad()
    guide = m.guidelines(padme, ('WB','NW', 'NE', 'EB')) #direction=(90,135,225,270))
    p, _  = m.collectPoints(padme, guide)
    s     = m.makeStripes(p)
    if self.VERBOSE: self.writer.plotLine(s, 't_meander_i')

'''
the
end
'''
