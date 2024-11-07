import unittest
import pprint
from flatten import Rectangle, Flatten, Parabola
pp = pprint.PrettyPrinter(indent=2)

############
# Parabola #
############

class Test(unittest.TestCase):
  def setUp(self):
    self.f = Flatten()
    self.done = Rectangle(x=2, y=2, w=3, h=3) # done is immutable

  def test_1(self):
    ''' north parabola from done
    '''
    expect = ([1,1,6,6,5,5,2,2,1], [4,6,6,4,4,5,5,4,4])
    seeker = Rectangle(x=1, y=4, w=5, h=2)
    self.done.plotPoints(seeker=seeker, fn='parabola_4')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    self.assertTrue(len(shapes))
    self.assertEqual(shapes[0].direction, 'N')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_2(self):
    ''' create south parabola from done
    '''
    expect = ([1,1,2,2,5,5,6,6,1], [1,3,3,2,2,3,3,1,1])
    seeker = Rectangle(x=1, y=1, w=5, h=2)
    self.done.plotPoints(seeker=seeker, fn='parabola_2')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    self.assertTrue(len(shapes))
    self.assertEqual(shapes[0].direction, 'S')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_3(self):
    ''' create west parabola from done
    '''
    expect = ([1,1,3,3,2,2,3,3,1], [1,6,6,5,5,2,2,1,1])
    seeker = Rectangle(x=1, y=1, w=2, h=5)
    self.done.plotPoints(seeker=seeker, fn='parabola_3')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    self.assertTrue(len(shapes))
    self.assertEqual(shapes[0].direction, 'W')
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_4(self):
    ''' east parabola
    '''
    expect = ([4,4,5,5,4,4,6,6,4], [1,2,2,5,5,6,6,1,1])
    seeker = Rectangle(x=4, y=1, w=2, h=5)
    self.done.plotPoints(seeker=seeker, fn='parabola_4')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    self.assertTrue(len(shapes))
    xy = shapes[0].boundary.xy
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_5(self):
    ''' west parabola meander
    '''
    expect = [
      (7, 1), (1, 1), (1, 2), (7, 2), (7, 3), (1, 3), (1, 4), (3, 4), (3, 5), (1, 5), (1, 6), (7, 6), (7, 7), (1, 7)
    ]
    done   = Rectangle(x=3,y=3,w=2,h=2)
    seeker = Rectangle(x=1,y=1,w=6,h=6)
    p = Parabola(seeker, done, direction='W')
    p.meander()
    p.plotPoints(fn='parabola_5', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_6(self):
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
    p.plotPoints(fn='parabola_6', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

'''
the
end
'''
