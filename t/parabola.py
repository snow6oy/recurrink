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

  def test_6(self):
    ''' southern parabola CCW=False
    '''
    expect = [ 
      (5,15),(5,5),(15,5),(15,6),(6,6),(6,15),(7,15),(7,7),
      (15,7),(15,9),(15,15),(14,15),(14,9),(13,9),(13,15)
    ]
    done   = Rectangle(x=8,y=8,w=4,h=8)
    seeker = Rectangle(x=4,y=4,w=12,h=12)
    p = Parabola(seeker, done, direction='S')
    p.meander()
    p.plotPoints(fn='parabola_6', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_7(self):
    ''' southern parabola CCW=True
    '''
    expect = [ 
      (15,2),(2,2),(2,15),(3,15),(3,3),(15,3),(15,4),(4,4),(4,15),(5,15),(5,5),
      (15,5),(15,7),(15,15),(14,15),(14,7),(13,7),(13,15),(12,15),(12,7)
    ]
    done   = Rectangle(x=6,y=6,w=5,h=10)
    seeker = Rectangle(x=1,y=1,w=15,h=15)
    p = Parabola(seeker, done, direction='S')
    p.meander()
    p.plotPoints(fn='parabola_7', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_8(self):
    ''' eastern meander with CCW False
    '''
    expect = [ 
      (1,17),(17,17),(17,1),(16,1),(16,16),(1,16),(1,15),(15,15),
      (15,1),(14,1),(14,14),(1,14),(1,13),(13,13),(13,1),(11,1),
      (1,1),(1,2),(11,2),(11,3),(1,3),(1,4),(11,4),(11,5),(1,5)
    ]
    done   = Rectangle(x=0,y=6,w=12,h=6)
    seeker = Rectangle(x=0,y=0,w=18,h=18)
    ''' CCW = True
    done   = Rectangle(x=1,y=6,w=10,h=5)
    seeker = Rectangle(x=1,y=1,w=15,h=15)
    '''
    p = Parabola(seeker, done, direction='E')
    p.meander()
    p.plotPoints(fn='parabola_8a', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_9(self):
    ''' eastern meander with CCW True
    '''
    done   = Rectangle(x=1,y=6,w=10,h=5)
    seeker = Rectangle(x=1,y=1,w=15,h=15)
    p = Parabola(seeker, done, direction='E')
    p.meander()
    p.plotPoints(fn='parabola_9', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual((15,2), xy[0])
    self.assertEqual((10,5), xy[-1])

  def test_10(self):
    ''' west meander CCW = False
    '''
    done   = Rectangle(x=7,y=7,w=12,h=6)
    seeker = Rectangle(x=1,y=1,w=18,h=18)
    p = Parabola(seeker, done, direction='W')
    p.meander()
    p.plotPoints(fn='parabola_10', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(xy[0],  (18,18))
    self.assertEqual(xy[-1], (18, 6))

  def test_11(self):
    ''' west parabola meander CCW = True
    '''
    expect = [
      (1,1),(1,14),(14,14),(14,13),(2,13),(2,1),(3,1),(3,12),(14,12),(14,11),(4,11),(4,1),
      (6,1),(6,4),(7,4),(7,1),(8,1),(8,4),(9,4),(9,1),(10,1),(10,4),(11,4),(11,1),(12,1),
      (12,4),(13,4),(13,1),(14,1),(14,4)
    ]
    ''' 
    done   = Rectangle(x=3,y=3,w=2,h=2)
    seeker = Rectangle(x=1,y=1,w=6,h=6)
    '''
    done   = Rectangle(x=5,y=5,w=10,h=5)
    seeker = Rectangle(x=0,y=0,w=15,h=15)
    p      = Parabola(seeker, done, direction='W')
    p.meander()
    p.plotPoints(fn='parabola_11', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_5(self):
    ''' north meander CCW False
    '''
    expect = [
      (5,5),(5,15),(15,15),(15,14),(6,14),(6,5),(7,5),(7,13),
      (15,13),(15,11),(15,5),(14,5),(14,11),(13,11),(13,5)
    ]
    done   = Rectangle(x=8,y=4,w=4,h=8)
    seeker = Rectangle(x=4,y=4,w=12,h=12)
    p = Parabola(seeker, done, direction='N')
    p.meander()
    p.plotPoints(fn='parabola_5', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual(expect, xy)

  def test_12(self):
    ''' north meander CCW True
    '''
    done   = Rectangle(x=6,y=1,w=5,h=10)
    seeker = Rectangle(x=1,y=1,w=15,h=15)
    p = Parabola(seeker, done, direction='N')
    p.meander()
    p.plotPoints(fn='parabola_12', boundary=False)
    xy = list(p.linefill.coords)
    self.assertEqual((15,15), xy[0])
    self.assertEqual((12,2), xy[-1])

'''
the
end
'''

