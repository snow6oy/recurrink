import unittest
import pprint
from flatten import Gnomon, Rectangle, Flatten
pp = pprint.PrettyPrinter(indent=2)

  ##########
  # Gnomon #
  ##########

class Test(unittest.TestCase):

  def setUp(self):
    self.f = Flatten()

  def test_0(self):
    ''' make a Gnomon from the bounding box dimensions of an outer and inner rectangle
    '''
    expect = [1, 1, 5, 5, 2, 2, 1]
    g = Gnomon((2,2,4,4), (1,1,5,5), direction='NW')
    x = list(g.boundary.xy[0])
    #pp.pprint(x)
    self.assertEqual(x, expect)

  def test_1(self):
    ''' north west gnomon meander 
    '''
    expect = [ 
      (1, 1),
      (1, 5),
      (2, 5),
      (2, 4),
      (3, 4),
      (3, 5),
      (4, 5),
      (4, 4),
      (5, 4),
      (5, 5)
    ]
    nw = Gnomon((2,2,4,4), (1,1,5,5), direction='NW')
    nw.meander()
    nw.plotPoints(fn='gnomon_1', boundary=False)
    xy = list(nw.linefill.coords)
    self.assertEqual(expect, xy)

  def test_2(self):
    ''' south east gnomon meander
    '''
    expect = [ 
      (2, 1),
      (8, 1),
      (8, 2),
      (2, 2),
      (2, 3),
      (8, 3),
      (8, 4),
      (6, 4),
      (6, 5),
      (8, 5),
      (8, 6),
      (6, 6)
    ]
    se = Gnomon((2,3,6,6), (0,1,8,8), direction='SE')
    se.meander()
    se.plotPoints(fn='gnomon_2', boundary=False)
    xy = list(se.linefill.coords)
    self.assertEqual(expect, xy)

  def test_3(self):
    ''' generate two gnomons from an embedded square
    '''
    count = 4
    expect_nw = ([1,1,5,5,2,2,1],[1,5,5,4,4,1,1])
    expect_se = ([2,2,4,4,5,5,2],[1,2,2,4,4,1,1])
    done   = Rectangle(x=1, y=1, w=4, h=4)
    seeker = Rectangle(x=2, y=2, w=2, h=2)
    shapes = self.f.overlayTwoCells(seeker, done)
    shapes[1].plotPoints(seeker=seeker, fn='gnomon_3')
    xy_nw = shapes[0].boundary.xy
    self.assertEqual(xy_nw[0].tolist(), expect_nw[0])
    self.assertEqual(xy_nw[1].tolist(), expect_nw[1])
    xy_se = shapes[1].boundary.xy
    self.assertEqual(xy_se[0].tolist(), expect_se[0])
    self.assertEqual(xy_se[1].tolist(), expect_se[1])

  def test_4(self):
    ''' overlay test: count rectangles embedded square
        also: does shapely return the expected boundary for our rectangle
    '''
    done   = Rectangle(x=1, y=1, w=4, h=4)
    seeker = Rectangle(x=2, y=2, w=2, h=2)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=seeker, fn='gnomon_4')
    [self.assertEqual(s.name, 'G') for s in shapes]

'''
the
end
'''
