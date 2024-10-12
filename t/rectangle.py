''' source v/bin/activate
    python -m unittest t.Test.test_n
'''
import unittest
import numpy as np
import pprint
from flatten import Rectangle, Flatten
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):
  def setUp(self):
    self.f = Flatten()

  def test_1(self):
    ''' does shapely return the expected boundary for our rectangle
    '''
    expect = np.array([[2, 2, 4, 4, 2], [2, 4, 4, 2, 2]])
    r = Rectangle(x=2, y=2, w=2, h=2)
    xy = np.array(r.xyPoints())
    self.assertEqual(xy.all(), expect.all())

  def test_2(self):
    ''' compare western edges: expect seeker max x to be greater than done max x
    '''
    done = Rectangle(x=0, y=0, w=3, h=3)
    seeker = Rectangle(x=1, y=0, w=3, h=3)
    self.assertTrue(seeker.w.bounds[0] > done.w.bounds[0])

  def test_3(self):
    ''' linefill is similar to boundary but used by Rectangle.meander()
    '''
    expect = [
      (1, 1),
      (7, 1),
      (7, 2),
      (1, 2),
      (1, 3),
      (7, 3),
      (7, 4),
      (1, 4),
      (1, 5),
      (7, 5),
      (7, 6),
      (1, 6),
      (1, 7),
      (7, 7)
    ]
    r = Rectangle(x=1, y=1, w=6, h=6, direction='E')
    r.meander()
    xy = list(r.linefill.coords)
    #pp.pprint(xy)
    self.assertEqual(expect, xy) 
    r.plotPoints(fn='rectangle_3', boundary=False)

  def test_4(self):
    ''' north square
    '''
    expect = [(0,0),(0,3),(1,3),(1,0),(2,0),(2,3),(3,3),(3,0)]
    r = Rectangle(x=0, y=0, w=3, h=3)
    r.meander()
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_4', boundary=False)
    self.assertEqual(expect, xy)

  def test_5(self):
    ''' east square
    '''
    expect = [(0,0),(3,0),(3,1),(0,1),(0,2),(3,2),(3,3),(0,3)]
    r = Rectangle(x=0, y=0, w=3, h=3, direction='E')
    r.meander()
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_5', boundary=False)
    self.assertEqual(expect, xy)

  def test_6(self):
    ''' north rectangle
    '''
    expect = [
      (3,1), (3,3), (4,3), (4,1), (5,1), (5,3), (6,3), (6,1), (7,1), (7,3), (8,3), (8,1)
    ]
    r = Rectangle(x=3, y=1, w=5, h=2)
    r.meander()
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_6', boundary=False)
    self.assertEqual(expect, xy)

  def test_7(self):
    ''' east rectangle
    '''
    expect = [(3,1), (8,1), (8,2), (3,2), (3,3), (8,3)]
    r = Rectangle(x=3, y=1, w=5, h=2, direction='E')
    r.meander()
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_7', boundary=False)
    self.assertEqual(expect, xy)

  def test_8(self):
    ''' north rectangle with uneven gaps
    '''
    expect = [(3,1),(3,14),(6,14),(6,1),(9,1),(9,14),(12,14),(12,1)]
    r = Rectangle(x=3, y=1, w=8, h=13)
    r.meander(gap=3)
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_8', boundary=False)
    self.assertEqual(expect, xy)

  def test_9(self):
    ''' east rectangle also with uneven gaps
    '''
    expect = [ 
      ( 3,  1),
      (11,  1),
      (11,  4),
      ( 3,  4),
      ( 3,  7),
      (11,  7),
      (11, 10),
      ( 3, 10),
      ( 3, 13),
      (11, 13),
      (11, 16),
      ( 3, 16)
    ]
    r = Rectangle(direction='E', x=3, y=1, w=8, h=13)
    r.meander(gap=3)
    xy = list(r.linefill.coords)
    r.plotPoints(fn='rectangle_9', boundary=False)
    self.assertEqual(expect, xy)

  def test_10(self):
    ''' count rectangles no overlap
    '''
    expect = 0
    expect_d = None
    done   = Rectangle(x=1, y=1, w=3, h=3)
    seeker = Rectangle(x=6, y=2, w=2, h=5)
    shapes = self.f.overlayTwoCells(done, seeker)
    self.assertEqual(expect, len(shapes))
    done.plotPoints(seeker=seeker, fn='rectangle_10')

  def test_11(self):
    ''' count rectangles no overlap with same row or col
    '''
    expect = 0
    expect_d = None
    done   = Rectangle(x=1, y=1, w=3, h=3)
    seeker = Rectangle(x=5, y=1, w=3, h=3)
    shapes = self.f.overlayTwoCells(done, seeker)
    self.assertEqual(len(shapes), expect)
    done.plotPoints(seeker=seeker, fn='rectangle_11')

  def test_12(self):
    ''' count rectangles large line
    '''
    expect = {
      'N': { 'x': [1, 1, 4, 4, 1], 'y': [3, 4, 4, 3, 3] },
      'S': { 'x': [1, 1, 4, 4, 1], 'y': [1, 2, 2, 1, 1] },
      'E': { 'x': [3, 3, 4, 4, 3], 'y': [1, 4, 4, 1, 1] },
      'W': { 'x': [1, 1, 2, 2, 1], 'y': [1, 4, 4, 1, 1] }
    }
    done = Rectangle(x=1, y=1, w=3, h=3)
    seekers = [
      Rectangle(x=0, y=2, w=5, h=1),
      Rectangle(x=2, y=0, w=1, h=5)
    ]
    for sk in seekers:
      shapes = self.f.overlayTwoCells(sk, done)
      for shape in shapes:
        d = shape.direction
        xy = shape.boundary.xy
        if d == 'W': # N and S are seeker 0
          shape.plotPoints(seeker=seekers[1], fn='rectangle_12')
          #pp.pprint(f"y {xy[1].tolist()}")
        self.assertEqual(expect[d]['x'], xy[0].tolist())
        self.assertEqual(expect[d]['y'], xy[1].tolist())

  def test_13(self):
    ''' count rectangles large square single corner
    '''
    expect = {
      'NW': { 'x': [3, 3, 6, 6, 5, 5, 3], 'y': [3, 6, 6, 4, 4, 3, 3] },
      'SE': { 'x': [1, 1, 4, 4, 6, 6, 1], 'y': [3, 5, 5, 8, 8, 3, 3] },
    }
    '''
      'NE': { 'x': [], 'y': [] }, # not implemented
      Rectangle(x= 1, y=1, w=3, h=3),
      'SW': { 'x': [], 'y': [] }  # not implemented
      Rectangle(x= 5, y=5, w=3, h=3)
    '''
    done = Rectangle(x=3, y=3, w=3, h=3)
    seekers = [
      Rectangle(x= 5, y=1, w=3, h=3),
      Rectangle(x= 1, y=5, w=3, h=3),
    ]
    for s in (seekers):
      shapes = self.f.overlayTwoCells(s, Rectangle(x=3, y=3, w=3, h=3))
      d = shapes[0].direction
      xy = shapes[0].boundary.xy
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])
    done.plotPoints(seeker=seekers[1], fn='rectangle_13')

  def test_14(self):
    ''' count rectangles large square almost covers all
        expect done rectangle to be north of seeker after overlay
    '''
    expect = {
      'N': { 'x':[2, 2, 5, 5, 2], 'y': [4, 5, 5, 4, 4] },
      'E': { 'x':[4, 4, 5, 5, 4], 'y': [2, 5, 5, 2, 2] },
      'S': { 'x':[2, 2, 5, 5, 2], 'y': [2, 3, 3, 2, 2] },
      'W': { 'x':[2, 2, 3, 3, 2], 'y': [2, 5, 5, 2, 2] }
    }
    done = Rectangle(x=2, y=2, w=3, h=3)
    seekers = [
      Rectangle(x=2, y=1, w=3, h=3),
      Rectangle(x=1, y=2, w=3, h=3),
      Rectangle(x=2, y=3, w=3, h=3),
      Rectangle(x=3, y=2, w=3, h=3)
    ]
    # new instance of done because otherwise box.bounds increments each time
    for s in seekers:
      shapes = self.f.overlayTwoCells(s, Rectangle(x=2, y=2, w=3, h=3))
      self.assertTrue(len(shapes))
      d = shapes[0].direction
      #pp.pprint(expect[d]['y'])
      xy = shapes[0].boundary.xy
      #pp.pprint(xy[1].tolist())
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])
    done.plotPoints(seeker=seekers[3], fn='rectangle_14')

  def test_15(self):
    ''' bounds are absolute
        dimensions are relative
        say it again!
    '''
    r = Rectangle(x=1, y=1, w=3, h=3)
    self.assertEqual((1.0, 1.0, 4.0, 4.0), r.box.bounds)
    self.assertEqual((1.0, 1.0, 3.0, 3.0), r.dimensions())

'''
the
end
'''
