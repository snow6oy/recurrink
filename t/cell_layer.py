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

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.VERBOSE = False
    self.writer  = SvgWriter()

  def test_a(self):
    ''' create a bg and check layer 0 is Polygon
    '''
    l = Layer()
    l.background(minkscape.cells['a'])
    self.assertEqual('Polygon', l.bft[0].geom_type)

  def test_b(self):
    ''' rectangle sqring defines the hole
        cell.layer.foreground assembles the parts
    '''
    l = Layer()
    geom = minkscape.cells['a']['geom']
    geom['name'] = 'sqring'
    l.background(minkscape.cells['a'])
    l.foreground(geom)
    p = MultiPolygon(l.bft)
    if self.VERBOSE: self.writer.plot(p, self.id())
 
  def test_c(self):
    ''' dimensions of three sizes
        given a pos 1 1
    ''' 
    expt = {
       'med': ( 9,  9, 18, 18),
      'smal': (12, 12, 15, 15),
      'lrge': ( 6,  6, 21, 21)
    }
    rslt         = dict()
    l            = Layer()
    dim          = l.dimension(x=1, y=1, clen=9)
    rslt['med']  = dim[:4]
    rslt['smal'] = dim[4:8]
    rslt['lrge'] = dim[8:]
    for size in ['med', 'smal', 'lrge']:
      self.assertEqual(expt[size], rslt[size])
    
  def test_d(self, x=0, y=0, stroke_width=0, clen=9):
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
    self.assertEqual((  9,  9), se)
    self.assertEqual((  9,  0), ne)
    self.assertEqual((  0,  9), sw)
    self.assertEqual((  0,  0), nw)
    self.assertEqual((4.5,4.5), mid)

  def test_e(self, x=0):
    ''' background alternates direction in Linear mode
    '''
    l = Layer(pos=tuple([x, 0]), linear=True)
    l.background(minkscape.cells['b'])

    linstr = l.bft[0]
    self.assertEqual('LineString', linstr.geom_type)
    if self.VERBOSE: self.writer.plotLine(linstr, self.id())

  def test_f(self): self.test_e(x=1)

'''
the
end
'''
