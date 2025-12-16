''' source v/bin/activate
    python -m unittest t.Test.test_n
'''
import unittest
import pprint
from cell import Layer
from cell.minkscape import *
from model import SvgWriter, SvgModel
from shapely.geometry import LinearRing, Polygon, MultiPolygon

class Test(unittest.TestCase):

  def setUp(self):
    self.VERBOSE = True
    self.writer  = SvgWriter()
    self.pp      = pprint.PrettyPrinter(indent=2)

  def test_a(self):
    ''' create a simple with bg and fg
    '''
    cell = Layer()
    cell.background(minkscape.cells['a'])
    cell.foreground(minkscape.cells['a']['geom'])
    mp = cell.polygon()
    self.assertEqual('MultiPolygon', mp.geom_type)

  def test_b(self):
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

  def test_c(self):
    ''' set clock migrated from Parabola
    '''
    l = Layer()
    self.assertFalse(l.setClock())  #12.0, 12.0))

  def test_d(self):
    ''' rectangle sqring defines the hole
        cell.layer.foreground assembles the parts
    '''
    cell = Layer()
    geom = minkscape.cells['a']['geom']
    geom['name'] = 'sqring'
    cell.background(minkscape.cells['a'])
    cell.foreground(geom)
    p = cell.polygon()
    if self.VERBOSE: self.writer.plot(p, self.id())
 
  def test_e(self):
    ''' dimensions of three sizes
        given a pos 1 1
    ''' 
    expt = {
       'med': ( 9,  9, 18, 18),
      'smal': (12, 12, 15, 15),
      'lrge': ( 6,  6, 21, 21)
    }
    rslt = dict()
    cell = Layer()
    dim  = cell.dimension(x=1, y=1, clen=9)
    rslt['med']  = dim[:4]
    rslt['smal'] = dim[4:8]
    rslt['lrge'] = dim[8:]
    for size in ['med', 'smal', 'lrge']:
      self.assertEqual(expt[size], rslt[size])
    
  def test_f(self, x=0, y=0, stroke_width=0, clen=9):
    ''' test some common points
        expect resuts based on SVG coordinates
        https://jenkov.com/tutorials/svg/svg-coordinate-system.html
    '''
    layer  = Layer()
    points = layer.points(x, y, stroke_width, clen)
    #self.pp.pprint(points)
    swd, cl, n, e, s, w, ne, se, nw, sw, mid = points
    self.assertEqual((4.5,   0), n)
    self.assertEqual((4.5,   9), s)
    self.assertEqual((  9,4.5),  e)
    self.assertEqual((  0,4.5),  w)
    self.assertEqual((  9,  9), ne)
    self.assertEqual((  9,  0), se)
    self.assertEqual((  0,  9), nw)
    self.assertEqual((  0,  0), sw)
    self.assertEqual((4.5,4.5), mid)

  def test_g(self, x=0):
    ''' background alternates direction in Linear mode
    '''
    cell = Layer(pos=tuple([x, 0]), linear=True)
    cell.background(minkscape.cells['a'])

    linstr = cell.bft[0]
    self.assertEqual('LineString', linstr.geom_type)
    if self.VERBOSE: self.writer.plotLine(linstr, self.id())

  def test_h(self): self.test_g(x=1)
  
  


