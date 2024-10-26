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

  def test_1(self):
    ''' north west gnomon meander 
    '''
    expect = [ 
      (1, 1), (1, 5), (2, 5), (2, 4), (3, 4), (3, 5), (4, 5), (4, 4), (5, 4), (5, 5)
    ]
    done   = Rectangle(x=2,y=2,w=2,h=2)
    seeker = Rectangle(x=1,y=1,w=4,h=4)
    nw = Gnomon(seeker, done, direction='NW')
    nw.meander()
    nw.plotPoints(fn='gnomon_1', boundary=False)
    xy = list(nw.linefill.coords)
    self.assertEqual(expect, xy)

  def test_2(self):
    ''' south east gnomon meander
    '''
    expect = [ 
      (2,1),(8,1),(8,2),(2,2),(2,3),(8,3),(8,4),(6,4),(6,5),(8,5),(8,6),(6,6)
    ]
    done   = Rectangle(x=2,y=3,w=4,h=3) 
    seeker = Rectangle(x=0,y=1,w=8,h=7)
    se = Gnomon(seeker, done, direction='SE')
    #done.plotPoints(seeker=seeker, fn='gnomon_2')
    se.meander()
    se.plotPoints(fn='gnomon_2', boundary=False)
    xy = list(se.linefill.coords)
    self.assertEqual(expect, xy)

  def test_3(self):
    ''' generate two gnomons from an embedded square
    '''
    expect_nw = ([1,1,5,5,2,2,1],[1,5,5,4,4,1,1])
    expect_se = ([2,2,4,4,5,5,2],[1,2,2,4,4,1,1])
    done   = Rectangle(x=2, y=2, w=2, h=2)
    seeker = Rectangle(x=1, y=1, w=4, h=4)
    shapes = self.f.overlayTwoCells(seeker, done)
    #done.plotPoints(seeker=seeker, fn='gnomon_3')
    done.plotPoints(seeker=shapes[1], fn='gnomon_3')
    xy_nw = shapes[0].boundary.xy
    self.assertEqual(xy_nw[0].tolist(), expect_nw[0])
    self.assertEqual(xy_nw[1].tolist(), expect_nw[1])
    xy_se = shapes[1].boundary.xy
    self.assertEqual(xy_se[0].tolist(), expect_se[0])
    self.assertEqual(xy_se[1].tolist(), expect_se[1])

  def test_4(self):
    ''' does overlay return gnomon labels
    '''
    expect = ['G000     1  1  5  5', 'G000     2  1  5  4']
    done   = Rectangle(x=2, y=2, w=2, h=2)
    seeker = Rectangle(x=1, y=1, w=4, h=4)
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=shapes[1], fn='gnomon_4')
    [self.assertEqual(s.label, expect[i]) for i, s in enumerate(shapes)]

  # TODO
  def test_5(self):
    ''' make a Gnomon from the bounding box dimensions of an outer and inner rectangle
    '''
    expect = [1, 1, 5, 5, 2, 2, 1]
    done   = Rectangle(x=2,y=2,w=4,h=4)
    seeker = Rectangle(x=1,y=1,w=5,h=5)
    done.plotPoints(seeker=seeker, fn='gnomon_5')
    g = Gnomon(seeker, done, direction='SE')
    x = list(g.boundary.xy[0])
    pp.pprint(x)
    #self.assertEqual(x, expect)

  def test_6(self):
    ''' count rectangles large square single corner split into two overlapping S + E
        NE and SW are not implemented
    '''
    expect = {
      'E': { 'x': [6, 6, 8, 8, 6], 'y': [1, 4, 4, 1, 1] },
      'S': { 'x': [5, 5, 8, 8, 5], 'y': [1, 3, 3, 1, 1] }
    }
    done   = Rectangle(x=3, y=3, w=3, h=3)
    seeker = Rectangle(x= 5, y=1, w=3, h=3)
    #done.plotPoints(seeker=seeker, fn='gnomon_5')
    shapes = self.f.overlayTwoCells(seeker, done)
    for s in shapes:
      d = s.direction
      #print(d)
      if d == 'S':
        done.plotPoints(seeker=s, fn='gnomon_6')
      xy = s.boundary.xy
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])

  def test_7(self):
    ''' not a gnomon from large square single corner
        but two rectangles
    '''
    expect = {
      'N': { 'x': [1, 1, 4, 4, 1], 'y': [6, 8, 8, 6, 6] },
      'W': { 'x': [1, 1, 3, 3, 1], 'y': [5, 8, 8, 5, 5] }
    }
    done   = Rectangle(x=3, y=3, w=3, h=3)
    seeker = Rectangle(x=1, y=5, w=3, h=3)
    #done.plotPoints(seeker=seeker, fn='gnomon_7')
    shapes = self.f.overlayTwoCells(seeker, done)
    for s in shapes:
      d = s.direction
      if d == 'N':
        done.plotPoints(seeker=s, fn='gnomon_7')
      xy = s.boundary.xy
      self.assertEqual(xy[0].tolist(), expect[d]['x'])
      self.assertEqual(xy[1].tolist(), expect[d]['y'])

'''
the
end
'''
