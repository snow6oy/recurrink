import unittest
import pprint
import matplotlib.pyplot as plt
import shapely.plotting
from shapely.geometry import Polygon, LinearRing, LineString
from cell import Meander, Plotter, Spiral
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):
  def setUp(self):
    self.writer  = Plotter()
    self.VERBOSE = True

  def test_a(self): 
    ''' guidelines for East with plot of before and after padding
    '''
    r       = Meander(Polygon([(3,3),(3,15),(15,15),(15,3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme,('EB','ET'))
    if self.VERBOSE: self.writer.plot(r.shape,padme,'t_meander_a')
    # [print(list(g.coords)) for g in list(guides.geoms)]
    g = list(guides.geoms)[0]
    self.assertEqual(g.coords[0],(4.0,4.0))

  def test_b(self): 
    ''' Rectangle with plot of stripes
    '''
    expect  = [(4,4),(14,14)]
    r       = Meander(Polygon([(3,3),(3,15),(15,15),(15,3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme,('EB','ET'))
    pnts    = r.collectPoints(padme,guides)
    stripes = r.makeStripes(pnts)
    first   = list(stripes.coords)[0]
    last    = list(stripes.coords)[-1]
    if self.VERBOSE: self.writer.plotLine(stripes,'t_meander_b')
    self.assertEqual(first,expect[0])
    self.assertEqual(last, expect[1])

  def test_c(self):
    ''' Gnomon
    '''
    g       = Meander(Polygon([(3,3),(3,15),(15,15),(15,11),(7,11),(7,3)]))
    padme   = g.pad()
    guides  = g.guidelines(padme,('WB','NW','NR'))  # (270,315,360))
    pnts    = g.collectPoints(padme,guides)
    stripes = g.makeStripes(pnts)
    if self.VERBOSE: self.writer.plotLine(stripes,'t_meander_c')
    self.assertEqual((6,4),list(stripes.coords)[0])
    self.assertEqual((14,14),list(stripes.coords)[-1])

  def test_d(self):
    ''' two Gnomons make a Polygon with a whole
    '''
    g      = Meander(Polygon([(3,3),(3,15),(7,15),(7,7),(15,7),(15,3)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad,('ET','NE','NR'))
    p1     = g.collectPoints(gpad,guides)
    gg     = Meander(Polygon([(11,7),(11,11),(7,11),(7,15),(15,15),(15,7)]))
    ggpad  = gg.pad()
    guides = gg.guidelines(ggpad,('NL','NE','EB'))
    p2     = g.collectPoints(ggpad,guides)
    stripe = g.joinStripes(p1,p2)
    if self.VERBOSE: self.writer.plotLine(stripe,'t_meander_d')
    xy     = list(stripe.coords)
    self.assertEqual((4,14),xy[0])
    self.assertEqual((8,12),xy[-1])

  def test_e(self):
    ''' one Gnomon plus Rectangle makes a Parabola
    '''
    g      = Meander(Polygon([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad,('WB','SW','SL')) 
    p1     = g.collectPoints(gpad,guides)
    r      = Meander(Polygon([(0,0),(0,12),(6,12),(6,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad,('NR','NL'))
    p2     = r.collectPoints(rpad,rguide)
    stripe = r.joinStripes(p1,p2)
    if self.VERBOSE: self.writer.plotLine(stripe,'t_meander_e')
    xy     = list(stripe.coords)
    self.assertEqual((17,1),xy[0])
    self.assertEqual((5,1),xy[-1])

  def test_f(self):
    ''' western Parabola
    '''
    g      = Meander(Polygon([(0,0),(0,18),(18,18),(18,12),(6,12),(6,0)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad,('SR','SE','EB')) #450,135,90))
    p1     = g.collectPoints(gpad,guides)
    r      = Meander(Polygon([(6,0),(6,6),(18,6),(18,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad,('WT','WB')) #  direction=(496,270))
    p2     = r.collectPoints(rpad,rguide)
    stripe = r.joinStripes(p1,p2)
    if self.VERBOSE: self.writer.plotLine(stripe,'t_meander_f')
    xy     = list(stripe.coords)
    self.assertEqual((17,17),xy[0])
    self.assertEqual((17,5),xy[-1])

  def test_g(self):
    ''' eastern Parabola
    '''
    g      = Meander(Polygon([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad,('SL','SW','WB'))  #direction=(180,225,270))
    p1     = g.collectPoints(gpad,guides)
    r      = Meander(Polygon([(0,0),(0,6),(12,6),(12,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad,('SL','SR')) # direction=(180,450)) 495,270))
    p2     = r.collectPoints(rpad,rguide)
    stripe = r.joinStripes(p1,p2)
    if self.VERBOSE: self.writer.plotLine(stripe,'t_meander_g')
    xy     = list(stripe.coords)
    self.assertEqual((1,17),xy[0])
    self.assertEqual((1,5),xy[-1])

  def test_h(self):
    ''' one Gnomon plus Rectangle makes a Parabola
        can join even number of stripes
    '''
    g      = Meander(Polygon([(0,8),(0,13),(13,13),(13,0),(8,0),(8,8)]))
    gpad   = g.pad()
    guides = g.guidelines(gpad,('SL','SW','WB')) #  direction=(180,225,270))
    p1     = g.collectPoints(gpad,guides)
    r      = Meander(Polygon([(0,0),(0,8),(4,8),(4,0)]))
    rpad   = r.pad()
    rguide = r.guidelines(rpad,('NR','NL')) # direction=(360,0))
    p2     = r.collectPoints(rpad,rguide)
    stripe = r.joinStripes(p1,p2)
    if self.VERBOSE: self.writer.plotLine(stripe,'t_meander_h')
    xy     = list(stripe.coords)
    self.assertEqual((1,12),xy[0])
    self.assertEqual((3,1),xy[-1])

  def test_i(self):
    ''' can NOT draw a north meander as a U-shape
         NW NE
        W     E
        it draws criss-cross because W and E are on the same axis
    '''
    m = Meander(Polygon([(1,1),(1,13),(13,13),(13,1),(9,1),(9,9),(5,9),(5,1)]))
    padme = m.pad()
    guide = m.guidelines(padme,('WB','NW','NE','EB'))
    p     = m.collectPoints(padme,guide)
    s     = m.makeStripes(p)
    if self.VERBOSE: self.writer.plotLine(s,'t_meander_i')

  def test_j(self):
    ''' check each guideline by comparing grid order
    '''
    expect = [
      ( 4, 5, 1, 4,15, 1),
      ( 4,15, 1, 4,15, 1),
      ( 4,15, 1, 4, 5, 1),
      ( 4,15, 1,14, 3,-1),
      ( 4, 5, 1,14, 3,-1),
      (14, 3,-1,14, 3,-1),
      (14, 3,-1, 4, 5, 1),
      (14,15, 1, 4,15, 1),
      ( 4,15, 1,14,15, 1),
      (14,15, 1,14, 3,-1),
      (14, 3,-1,14,15, 1),
      (14, 3,-1, 4,15, 1) 
    ]
    d       = ('NL','NE','EB','SE','SL','SW','WB','NR','ET','SR','WT')
    r       = Meander(Polygon([(3,3),(3,15),(15,15),(15,3)]))
    padme   = r.pad()
    guides  = r.guidelines(padme,direction=d)
    for i,g in enumerate(list(guides.geoms)):
      grid_ord = r.orderGrid(g)
      self.assertEqual(expect[i],grid_ord)

  def test_k(self):
    ''' koto fails on sw gnomon

        theory 1. orderGrid always generates integers
                  but guidelines can be floats 
                  this causes points to miss guidelines
        theory 2. padding creates rectangles, but squares are needed

      [(6.5,16.0),(6.5,21.5),(8.5,21.5),(8.5,23.5),
       (14.0,23.5),(14.0,16.0),(6.5,16.0)]
    '''
    g     = Polygon(
      [(6,16.0),(6,21),(8,21),(8,23),(13.0,23),(13.0,16.0),(6,16.0)]
    )
    self.writer.plot(g,g,fn='t_meander_k')
    m     = Meander(g)
    guide = m.guidelines(g,('SL','SE','ET'))
    line    = m.collectPoints(g,guide)
    stripes = m.makeStripes(line)
    if self.VERBOSE: 
      self.writer.plotGuideLines(guide, fn='t_meander_k')
      self.writer.plotLine(stripes, fn='t_meander_kk')
    self.assertEqual(18, len(list(stripes.coords)))

  def test_l(self):
    ''' set clock migrated from Parabola
    '''
    m = Meander(Polygon())
    self.assertFalse(m.setClock(12.0, 12.0))
    self.assertTrue(m.setClock(15.0, 15.0))

  def test_m(self):
    ''' random sample points with some edge cases
    '''
    s = Spiral()
    assert s.r1( 0, 0, 3)[ 3] == [0, 2]
    assert s.r1( 8, 1, 3)[ 9] == [1, 1]
    assert s.r1(16, 1, 5)[19] == [1, 3]
    assert s.r1( 0, 0, 4)[ 4] == [0, 3]

    assert s.c1( 3, 0, 3)[ 5] == [2, 2]
    assert s.c1(14, 1, 4)[15] == [2, 2]
    assert s.c1( 5, 0, 5)[ 9] == [4, 4]
    assert s.c1(19, 1, 5)[21] == [3, 3]

    assert s.r2( 5, 0, 3)[ 7] == [2, 0]
    assert s.r2( 7, 0, 4)[10] == [3, 0]
    assert s.r2(15, 1, 4)[16] == [2, 1]
    assert s.r2(21, 1, 5)[23] == [3, 1]

    assert s.c2( 7, 0, 3)[ 8] == [1, 0]
    assert s.c2(10, 0, 4)[12] == [1, 0]
    assert s.c2(23, 1, 5)[24] == [2, 1]
    assert s.c2(30, 1, 6)[32] == [2, 1]

  def test_n(self):
    LEN     = 9 # length of matrix 
    s       = Spiral()
    spiral  = s.matrix(LEN)
    self.assertEqual(81, len(list(spiral)))
    if self.VERBOSE:
      fig, ax = plt.subplots() 
      shapely.plotting.plot_line(LineString(spiral), ax=ax)
      plt.savefig(f"tmp/t_meander_n.svg", format="svg")

  def test_o(self):
    ''' split spiral into many lines according to the shape of a hole
    '''
    outer  = [(0,0), (9,0), (9,9), (0,9)]
    inner  = [(4,2), (4,7), (7,7), (7,2)]
    small  = Polygon(outer, holes=[inner])
    m      = Meander(small)
    spiral = m.spiral(clen=10)
    self.assertEqual(2, len(spiral.geoms))
    if self.VERBOSE:
      self.writer.plotLine(spiral, self.id())
      '''
      print(self.id())
      fig, ax = plt.subplots() 
      shapely.plotting.plot_line(spiral, ax=ax, linewidth=0.5)
      plt.savefig(f"tmp/t_meander_o.svg", format="svg")
      '''

  def test_q(self):
    ''' split spiral into many lines according to the shape of a hole
    '''
    outer = [(0,0), (3,0), (3,3), (0,3)]
    inner = [(1,1), (1,2), (2,2), (2,1)]
    small = Polygon(outer, holes=[inner])
    m     = Meander(small)
    line  = m.matrix(4)
    mls   = m.splitLines(line, Polygon(inner)) #small.interiors[0])
    self.assertEqual(1, len(mls.geoms))

  def test_p(self):
    ''' split on a 15 x 15 cell
    '''
    outer = [(0,0), (15,0), (15,15), (0,15)]
    inner = [(4,3), (4,11), (10,11), (10,3)]
    p15   = Polygon(outer, holes=[inner])
    m     = Meander(p15)
    s     = m.spiral(15)

    l2_begin = list(s.geoms[1].coords)[0]
    self.assertEqual((11,11), l2_begin)

    l2_end   = list(s.geoms[1].coords)[-1]
    self.assertEqual((10,3), l2_end)

  def test_r(self):
    ''' irregular sqring needs a spiral
    '''
    outer = [(0,0), (60,0), (60,60), (0,60)]
    inner = [(20,15), (20,45), (40,45), (40,15)]
    wonky = Polygon(outer, holes=[inner])
    m     = Meander(wonky)
    line  = m.matrix(60)
    mls   = m.splitLines(line, Polygon(inner)) #small.interiors[0])

    #for g in mls.geoms: print(list(g.coords))

    if self.VERBOSE:
      print(self.id())
      fig, ax = plt.subplots() 
      ax.axes.get_xaxis().set_visible(False)
      ax.axes.get_yaxis().set_visible(False)

      shapely.plotting.plot_line(
        #LineString(line), ax=ax, linewidth=2, add_points=False
        mls, ax=ax, linewidth=2, add_points=False
      )
      plt.savefig(f"tmp/t_meander_r.svg", format="svg")
