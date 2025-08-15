import unittest
import pprint
from shapely.geometry import Polygon
from cell.shape import Parabola
from model import SvgWriter
pp = pprint.PrettyPrinter(indent=2)
############
# Parabola #
############

class Test(unittest.TestCase):

  def setUp(self):
    self.p       = Parabola()
    self.writer  = SvgWriter()
    self.VERBOSE = True

  def test_a(self):
    ''' start simple
    '''
    self.assertEqual(self.p.name, 'parabola')

  def test_b(self):
    ''' south parabola contructs ok with cell length 15
    '''
    kwargs = {'facing': 'south', 'size': 'medium'}
    dim    = (0, 0, 14, 14, 5, 5, 10, 10)
    coords = self.p.coords(dim, kwargs)
    if self.VERBOSE: self.writer.plot(Polygon(coords), self.id())

  def test_c(self):
    expect = [
      ('composite', 'NE', 'west'),
      ('composite', 'SW', 'east'),
      ('composite', 'SE', 'north'),
      ('composite', 'NW', 'south')
    ]
    for i, d in enumerate(['N', 'S', 'E', 'W']):
      g = self.p.guide(d)
      self.assertEqual(expect[i][1], g[1])

  def test_3(self):
    ''' west
    expect = ([0,0,3,3,2,2,3,3,0], [0,3,3,2,2,1,1,0,0])
    done   = Rectangle(x=2, y=1, w=3, h=1)
    seeker = Rectangle(x=0, y=0, w=3, h=3)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_3')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])
    '''

  def test_4(self):
    ''' north parabola
    expect = ([1,1,7,7,5,5,3,3,1], [1,3,3,1,1,2,2,1,1])
    seeker = Rectangle(x=3, y=0, w=2, h=2)
    done   = Rectangle(x=1, y=1, w=6, h=2)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_4')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])
    '''

  def test_5(self):
    ''' east parabola
    expect = ([1,1,2,2,1,1,4,4,1], [0,1,1,2,2,3,3,0,0])
    done   = Rectangle(x=0, y=1, w=2, h=1)
    seeker = Rectangle(x=1, y=0, w=3, h=3)
    done.plotPoints(seeker=seeker, fn='parabola_5')
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_5')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])
    '''

  def test_6(self):
    ''' parabola meander with direction=W
    expect = [
      (7, 1), (1, 1), (1, 2), (7, 2), (7, 3), (1, 3), (1, 4), (3, 4), (3, 5), (1, 5), (1, 6), (7, 6), (7, 7), (1, 7)
    ]
    done   = Rectangle(x=3,y=3,w=2,h=2)
    seeker = Rectangle(x=1,y=1,w=6,h=6)
    p = Parabola(seeker, done, direction='W')
    p.meander()
    p.plotPoints(fn='parabola_6', boundary=False)
    xy = list(p.linefill.coords)
    #pp.pprint(xy)
    self.assertEqual(expect, xy)
    '''

  def test_7(self):
    ''' southern parabola 
    expect = [ 
      (1,11),(1,1),(11,1),(11,2),(2,2),(2,11),(3,11),(3,3),
      (11,3),(11,5),(11,11),(10,11),(10,5),(9,5),(9,11)
    ]
    a = CellMaker((0,0), clen=12)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(4,4), (4,12), (8,12), (8,4), (4,4)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    #a.bft[0].padme()
    #a.bft[1].padme()
    xy = a.bft[0].this.lineFill(facing='south')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_a')
    self.assertEqual(expect, list(xy.coords))
    if self.VERBOSE: self.writer.plot(a.bft[0].this.data,b, fn='t_parabola_a')
    '''

  def test_b(self):
    ''' southern parabola CCW=True
    expect = [ 
      (14,1),(1,1),(1,14),(2,14),(2,2),(14,2),(14,3),
      (3,3),(3,14),(4,14),(4,4),(14,4),(14,6),(14,14),
      (13,14),(13,6),(12,6),(12,14),(11,14),(11,6)
    ]
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,5), (5,15), (10,15), (10,5), (5,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='south')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_b')
    self.assertEqual(expect, list(xy.coords))
    '''

  def test_c(self):
    ''' eastern meander with CCW False
    expect = [ 
      (1,17),(17,17),(17,1),(16,1),(16,16),(1,16),(1,15),(15,15),
      (15,1),(14,1),(14,14),(1,14),(1,13),(13,13),(13,1),(11,1),
      (1,1),(1,2),(11,2),(11,3),(1,3),(1,4),(11,4),(11,5),(1,5)
    ]
    a = CellMaker((0,0), clen=18)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(0,6), (0,12), (12,12), (12,6), (0,6)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='east')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_c')
    self.assertEqual(expect, list(xy.coords))
    '''

  def test_d(self):
    ''' eastern meander with CCW True
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(0,5), (0,10), (10,10), (10,5), (0,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='east')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_d')
    self.assertEqual((14,1), list(xy.coords)[0])
    self.assertEqual((9,4), list(xy.coords)[-1])
    '''

  def test_e(self):
    ''' west meander CCW = False
    a = CellMaker((0,0), clen=18)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(6,6), (18,6), (18,12), (6,12), (6,6)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='west')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_e')
    self.assertEqual((17,17), list(xy.coords)[0])
    self.assertEqual((17,5),  list(xy.coords)[-1])
    '''

  def test_f(self):
    ''' west parabola meander CCW = True
    expect = [
      (1,1),(1,14),(14,14),(14,13),(2,13),(2,1),(3,1),
      (3,12),(14,12),(14,11),(4,11),(4,1),(6,1),(6,4),
      (7,4),(7,1),(8,1),(8,4),(9,4),(9,1),(10,1),(10,4),
      (11,4),(11,1),(12,1),(12,4),(13,4),(13,1),(14,1),(14,4)
    ]
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,5), (5,10), (15,10), (15,5), (5,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='west')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_f')
    self.assertEqual(expect, list(xy.coords))
    '''

  def test_g(self):
    ''' north meander CCW False
    expect = [
      (1,1),(1,11),(11,11),(11,10),(2,10),(2,1),(3,1),(3,9),
      (11,9 ),(11,7 ),(11,1),(10,1),(10,7 ),(9 ,7 ),(9 ,1)
    ]
    a = CellMaker((0,0), clen=12)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(4,0), (4,8), (8,8), (8,0), (4,0)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='north')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_g')
    self.assertEqual(expect, list(xy.coords))
    '''

  def test_h(self):
    ''' north meander CCW True
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,0), (5,10), (10,10), (10,0), (5,0)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='north')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_h')
    self.assertEqual((14,14), list(xy.coords)[0])
    self.assertEqual((11,1), list(xy.coords)[-1])
    '''
'''
the
end
'''
