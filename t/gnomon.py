import unittest
import pprint
from shapes import Gnomon, Rectangle
from flatten import Flatten
pp = pprint.PrettyPrinter(indent=2)

  ##########
  # Gnomon #
  ##########

class Test(unittest.TestCase):

  def setUp(self):
    self.f    = Flatten()
    self.done = Rectangle(x=2,y=2,w=3,h=3)

  def test_1(self):
    ''' north west gnomon meander 
    '''
    expect = [(2, 1), (2, 5), (6, 5), (6, 6), (1, 6), (1, 1)]
    seeker = Rectangle(x=1,y=1,w=5,h=5)
    nw = Gnomon(seeker, self.done, direction='NW')
    nw.meander()
    nw.plotPoints(fn='gnomon_1', boundary=False)
    xy = list(nw.linefill.coords)
    self.assertEqual(expect, xy)

  def test_2(self):
    ''' south east gnomon meander
    '''
    expect = [
      (2.0, 2.0), (5.0, 2.0), (5.0, 5.0), (6.0, 5.0), (6.0, 1.0), (2.0, 1.0)
    ]
    seeker = Rectangle(x=1,y=1,w=5,h=5)
    #self.done.plotPoints(seeker=seeker, fn='gnomon_2')
    se = Gnomon(seeker, self.done, direction='SE')
    se.meander()
    se.plotPoints(fn='gnomon_2', boundary=False)
    xy = list(se.linefill.coords)
    self.assertEqual(expect, xy)

  def test_3(self):
    ''' generate two gnomons from an embedded square and test boundary
    '''
    expect_nw = ([1,1,6,6,2,2,1],[1,6,6,5,5,1,1])
    expect_se = ([2,2,5,5,6,6,2],[1,2,2,5,5,1,1])
    seeker = Rectangle(x=1, y=1, w=5, h=5)
    shapes = self.f.overlayTwoCells(seeker, self.done)
    xy_nw = shapes[0].boundary.xy
    self.assertEqual(xy_nw[0].tolist(), expect_nw[0])
    self.assertEqual(xy_nw[1].tolist(), expect_nw[1])
    xy_se = shapes[1].boundary.xy
    self.assertEqual(xy_se[0].tolist(), expect_se[0])
    self.assertEqual(xy_se[1].tolist(), expect_se[1])

  def test_4(self):
    ''' does overlay return gnomon labels
    '''
    expect = ['G000     1  1  6  6', 'G000     2  1  6  5']
    done   = Rectangle(x=2, y=2, w=2, h=2)
    seeker = Rectangle(x=1, y=1, w=5, h=5)
    shapes = self.f.overlayTwoCells(seeker, self.done)
    #self.done.plotPoints(seeker=shapes[1], fn='gnomon_4')
    [self.assertEqual(s.label, expect[i]) for i, s in enumerate(shapes)]

  def test_5(self):
    ''' make a Gnomon from the bounding box dimensions of an outer and inner rectangle
    '''
    expect = [2, 2, 5, 5, 6, 6, 2]
    seeker = Rectangle(x=1,y=1,w=5,h=5)
    self.done.plotPoints(seeker=seeker, fn='gnomon_5')
    g = Gnomon(seeker, self.done, direction='SE')
    x = list(g.boundary.xy[0])
    self.assertEqual(x, expect)

  def test_6(self):
    ''' count rectangles large square single corner split into two rectangles
        originally S + E but now E + W ??
    '''
    expect = {
      'E': { 'x': [5, 5, 6, 6, 5], 'y': [1, 4, 4, 1, 1] },
      'W': { 'x': [2, 2, 3, 3, 2], 'y': [1, 4, 4, 1, 1] }
    }
    seeker = Rectangle(x=3, y=1, w=3, h=3)
    self.done.plotPoints(seeker=seeker, fn='gnomon_6')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    self.assertEqual(len(shapes), 2)
    for s in shapes:
      d = s.direction
      self.assertTrue(d in list(expect.keys()))
      xy = s.boundary.xy
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])

  def test_7(self):
    ''' not a gnomon from large square single corner
        but two rectangles
    '''
    expect = {
      'E': { 'x': [4, 4, 5, 5, 4], 'y': [3, 6, 6, 3, 3] },
      'S': { 'x': [1, 1, 4, 4, 1], 'y': [2, 3, 3, 2, 2] }
    }
    seeker = Rectangle(x=1, y=3, w=3, h=3)
    self.done.plotPoints(seeker=seeker, fn='gnomon_7')
    shapes = self.f.overlayTwoCells(seeker, self.done)
    for s in shapes:
      d = s.direction
      self.assertTrue(d in list(expect.keys()), 'unknown direction')
      if False:
        self.done.plotPoints(seeker=s, fn='gnomon_7')
      xy = s.boundary.xy
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])
'''
the
end
'''
