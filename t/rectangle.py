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
    shapes = self.f.overlayTwoCells(seeker, done) # TODO ds swap
    self.assertEqual(expect, len(shapes))
    done.plotPoints(seeker=seeker, fn='rectangle_10')

  def test_11(self):
    ''' count rectangles no overlap with same row or col
    '''
    expect = 0
    done   = Rectangle(x=1, y=1, w=3, h=3)
    seeker = Rectangle(x=5, y=1, w=3, h=3)
    shapes = self.f.overlayTwoCells(seeker, done)
    self.assertEqual(len(shapes), expect)
    done.plotPoints(seeker=seeker, fn='rectangle_11')

  def test_12(self):
    ''' count rectangles large line
        this test splits seeker in two
        to avoid printing all permutations, rerun test afer tweaking 
    '''
    expect = {
      'N': { 'x': [1, 1, 4, 4, 1], 'y': [3, 4, 4, 3, 3] },
      'S': { 'x': [1, 1, 4, 4, 1], 'y': [1, 2, 2, 1, 1] },
      'E': { 'x': [3, 3, 4, 4, 3], 'y': [1, 4, 4, 1, 1] },
      'W': { 'x': [1, 1, 2, 2, 1], 'y': [1, 4, 4, 1, 1] }
    }
    seeker = Rectangle(x=1, y=1, w=3, h=3)
    done = [
      Rectangle(x=0, y=2, w=5, h=1), # Done is EW and Seeker requires NS split
      Rectangle(x=2, y=0, w=1, h=5)  # EW split
    ]
    #done[1].plotPoints(seeker=seeker, fn='rectangle_12')
    for d in done:
      shapes = self.f.overlayTwoCells(seeker, d)
      for shape in shapes:
        dn = shape.direction
        xy = shape.boundary.xy
        if dn == 'z': # NSEW
          print(dn)
          pp.pprint(f"y {expect[dn]['y']}")
          pp.pprint(f"y {xy[1].tolist()}")
          d.plotPoints(seeker=shape, fn='rectangle_12')
        self.assertEqual(expect[dn]['x'], xy[0].tolist())
        self.assertEqual(expect[dn]['y'], xy[1].tolist())

  def test_14(self):
    ''' count rectangles large square almost covers all
        expect done rectangle to be north of seeker after overlay
    '''
    expect = {
      'N': { 'x':[2, 2, 5, 5, 2], 'y': [5, 6, 6, 5, 5] },
      'E': { 'x':[5, 5, 6, 6, 5], 'y': [2, 5, 5, 2, 2] },
      'S': { 'x':[2, 2, 5, 5, 2], 'y': [1, 2, 2, 1, 1] },
      'W': { 'x':[1, 1, 2, 2, 1], 'y': [2, 5, 5, 2, 2] }
    }
    done = Rectangle(x=2, y=2, w=3, h=3)
    seekers = [
      Rectangle(x=2, y=3, w=3, h=3),
      Rectangle(x=3, y=2, w=3, h=3),
      Rectangle(x=2, y=1, w=3, h=3),
      Rectangle(x=1, y=2, w=3, h=3)
    ]
    # new instance of done because otherwise box.bounds increments each time
    #done.plotPoints(seeker=seekers[0], fn='rectangle_14')
    for s in seekers:
      shapes = self.f.overlayTwoCells(s, done) # Rectangle(x=2, y=2, w=3, h=3))
      self.assertTrue(len(shapes))
      d = shapes[0].direction
      xy = shapes[0].boundary.xy
      if d == 'z':
        print(d)
        pp.pprint(expect[d]['y'])
        pp.pprint(xy[1].tolist())
        done.plotPoints(seeker=shapes[0], fn='rectangle_14')
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])

  def test_15(self):
    ''' bounds are absolute
        dimensions are relative
        say it again!
    '''
    r = Rectangle(x=1, y=1, w=3, h=3)
    self.assertEqual((1.0, 1.0, 4.0, 4.0), r.box.bounds)
    self.assertEqual((1.0, 1.0, 3.0, 3.0), r.dimensions())

  def test_16(self):
    ''' compare a rectangle against itself
    '''
    r = Rectangle(x=20,y=10,w=50,h=10)
    shapes = self.f.overlayTwoCells(r, r)
    self.assertFalse(len(shapes))

  def test_17(self):
    ''' touching rectangles cannot be split
    '''
    #print(self.id())
    done = Rectangle(x=1,y=1,w=1,h=1)
    seekers = [ 
      Rectangle(x=1,y=0,w=1,h=1), # NORTH
      Rectangle(x=1,y=2,w=1,h=1), # SOUTH
      Rectangle(x=0,y=1,w=1,h=1), # EAST
      Rectangle(x=2,y=1,w=1,h=1)  # WEST
    ]
    for s in seekers:
      shapes = self.f.overlayTwoCells(s, done)
      self.assertFalse(len(shapes))
    done.plotPoints(seeker=seekers[0], fn='rectangle_17')
'''
the
end
'''
