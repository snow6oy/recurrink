import unittest
from shapely.geometry import Polygon
from cell.shape import Parabola
from model import SvgWriter
'''
import pprint
from flatten import Rectangle, Flatten, Parabola
pp = pprint.PrettyPrinter(indent=2)
'''
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

  def test_3(self):
    ''' west
    '''
    expect = ([0,0,3,3,2,2,3,3,0], [0,3,3,2,2,1,1,0,0])
    done   = Rectangle(x=2, y=1, w=3, h=1)
    seeker = Rectangle(x=0, y=0, w=3, h=3)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_3')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_4(self):
    ''' north parabola
    '''
    expect = ([1,1,7,7,5,5,3,3,1], [1,3,3,1,1,2,2,1,1])
    seeker = Rectangle(x=3, y=0, w=2, h=2)
    done   = Rectangle(x=1, y=1, w=6, h=2)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_4')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_5(self):
    ''' east parabola
    '''
    expect = ([1,1,2,2,1,1,4,4,1], [0,1,1,2,2,3,3,0,0])
    done   = Rectangle(x=0, y=1, w=2, h=1)
    seeker = Rectangle(x=1, y=0, w=3, h=3)
    done.plotPoints(seeker=seeker, fn='parabola_5')
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[0], fn='parabola_5')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_6(self):
    ''' parabola meander with direction=W
    '''
    expect = [
      (7, 1), (1, 1), (1, 2), (7, 2), (7, 3), (1, 3), (1, 4), (3, 4), (3, 5), (1, 5), (1, 6), (7, 6), (7, 7), (1, 7)
    ]
    done   = Rectangle(x=3,y=3,w=2,h=2)
    seeker = Rectangle(x=1,y=1,w=6,h=6)
    ''' 
    done   = Rectangle(x=10,y=10,w=70,h=10)
    seeker = Rectangle(pencolor='FFF', x=0,y=0,w=30,h=30)
    '''
    p = Parabola(seeker, done, direction='W')
    p.meander()
    p.plotPoints(fn='parabola_6', boundary=False)
    xy = list(p.linefill.coords)
    #pp.pprint(xy)
    self.assertEqual(expect, xy)

  def test_7(self):
    ''' southern parabola 
    '''
    expect = [ 
      (2, 6), (2, 6), (3, 6), (3, 2), (4, 2), (4, 4), (5, 4), 
      (5, 2), (6, 2), (6, 4), (7, 4), (7, 2), (8, 2), (8, 6)
    ]
    done   = Rectangle(x=4,y=4,w=2,h=2)
    seeker = Rectangle(x=2,y=2,w=6,h=4)
    p = Parabola(seeker, done, direction='S')
    p.meander()
    p.plotPoints(fn='parabola_7', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)
'''
the
end
'''
