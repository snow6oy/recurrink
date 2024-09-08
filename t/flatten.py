#!/usr/bin/env python3
''' python3 -m unittest t.TestGeomink.testn
'''
import unittest
import pprint
from flatten import Flatten, Rectangle, Gnomon, Parabola
pp = pprint.PrettyPrinter(indent=2)

class TestFlatten(unittest.TestCase):

  def setUp(self):
    self.f  = Flatten()
    #self.positions = config.positions
    #elf.data = config.cells
  def test_0(self):
    ''' north square
    '''
    expect = ([0, 0, 1, 1, 2, 2, 3, 3], [0, 3, 3, 0, 0, 3, 3, 0])
    r = Rectangle(coordinates=(0, 0), dim=(3, 3))
    r.meander()
    #r.printPoints()
    self.assertEqual(len(expect[0]), len(r.xyPoints()[0]))
    self.assertEqual(expect, r.xyPoints())
  def test_1(self):
    ''' east square
    '''
    expect = ([0, 3, 3, 0, 0, 3, 3, 0], [0, 0, 1, 1, 2, 2, 3, 3])
    r = Rectangle(coordinates=(0, 0), dim=(3, 3), direction='E')
    r.meander()
    self.assertEqual(expect, r.xyPoints())
  def test_2(self):
    ''' north rectangle
    '''
    expect = ([3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8], [1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1])
    r = Rectangle(coordinates=(3, 1), dim=(5, 2))
    r.meander()
    self.assertEqual(len(expect[0]), len(r.xyPoints()[0]))
    self.assertEqual(expect, r.xyPoints())
  def test_3(self):
    ''' east rectangle
    '''
    expect = ([3, 8, 8, 3, 3, 8], [1, 1, 2, 2, 3, 3])
    r = Rectangle(coordinates=(3, 1), dim=(5, 2), direction='E')
    r.meander()
    self.assertEqual(expect, r.xyPoints())
  def test_4(self):
    ''' north rectangle with uneven gaps
    '''
    expect = ([3, 3, 6, 6, 9, 9, 12, 12], [1, 14, 14, 1, 1, 14, 14, 1])
    r = Rectangle(coordinates=(3, 1), dim=(8, 13), direction='N')
    r.meander(gap=3)
    self.assertEqual(expect, r.xyPoints())
  def test_5(self):
    ''' east rectangle also with uneven gaps
    '''
    expect = ([3, 11, 11, 3, 3, 11, 11, 3, 3, 11, 11, 3], [1, 1, 4, 4, 7, 7, 10, 10, 13, 13, 16, 16])
    r = Rectangle(coordinates=(3, 1), dim=(8, 13), direction='E')
    r.meander(gap=3)
    self.assertEqual(len(expect[0]), len(r.xyPoints()[0]))
    self.assertEqual(expect, r.xyPoints())
  # Overlay tests
  def test_6(self):
    ''' count rectangles embedded square
    '''
    expect = 4
    count, d = self.f.overlayTwoCells(
      Rectangle(coordinates=(0, 0), dim=(4, 4)),
      Rectangle(coordinates=(1, 1), dim=(2, 2))
    )
    self.assertEqual(expect, count)
  def test_7(self):
    ''' count rectangles U shapes
    '''
    expect = 3
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    upper = [
      Rectangle(coordinates=(-2,  1), dim=(3, 1)),
      Rectangle(coordinates=( 1,  2), dim=(1, 3)),
      Rectangle(coordinates=( 2,  1), dim=(3, 1)),
      Rectangle(coordinates=( 1, -2), dim=(1, 3))
    ]
    for u in upper:
      count, d = self.f.overlayTwoCells(lower, u)
      self.assertEqual(expect, count)
  def test_8(self):
    ''' count rectangles large line
    '''
    expect = 2
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    upper = [
      Rectangle(coordinates=(-1,  1), dim=(5, 1)),
      Rectangle(coordinates=( 1, -1), dim=(1, 5))
    ]
    for u in upper:
      count, d = self.f.overlayTwoCells(lower, u)
      self.assertEqual(expect, count)
  def test_9(self):
    ''' count rectangles large square single corner
    '''
    expect = 2
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    upper = [
      Rectangle(coordinates=(-2, -2), dim=(3, 3)),
      Rectangle(coordinates=( 2,  2), dim=(3, 3)),
      Rectangle(coordinates=(-2,  2), dim=(3, 3)),
      Rectangle(coordinates=( 2, -2), dim=(3, 3))
    ]
    for u in upper:
      count, d = self.f.overlayTwoCells(lower, u)
      self.assertEqual(expect, count)
  def test_10(self):
    ''' count rectangles large square almost covers all
    '''
    expect = 1
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    upper = [
      Rectangle(coordinates=( 0, -1), dim=(3, 3)),
      Rectangle(coordinates=(-1,  0), dim=(3, 3)),
      Rectangle(coordinates=( 0,  1), dim=(3, 3)),
      Rectangle(coordinates=( 1,  0), dim=(3, 3))
    ]
    for u in upper:
      count, d = self.f.overlayTwoCells(lower, u)
      self.assertEqual(expect, count)
  def test_11(self):
    ''' up western edge is within the boundary of lower
    '''
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    up = Rectangle(coordinates=(1, 0), dim=(3, 3))
    up.compare(lower)
    self.assertTrue(up.WEDG)
  def test_12(self):
    ''' up western edge is NOT within the boundary of lower
    '''
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    up = Rectangle(coordinates=(0, 4), dim=(3, 3))
    up.compare(lower)
    self.assertFalse(up.WEDG)
  def test_13(self):
    ''' count rectangles no overlap
    '''
    expect = 0
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    count, d = self.f.overlayTwoCells(lower, 
      Rectangle(coordinates=( 9,  1), dim=(3, 3))
    )
    self.assertEqual(expect, count)

  def test_14(self):
    ''' count rectangles no overlap with same row or col
    '''
    expect = 0
    lower = Rectangle(coordinates=(0, 0), dim=(3, 3))
    up = Rectangle(coordinates=(0, 6), dim=(3, 3))
    count, d = self.f.overlayTwoCells(lower, up)
    '''
    print(up.NEDG)
    print(up.EEDG)
    print(up.SEDG)
    print(up.WEDG)
    '''
    self.assertEqual(expect, count)

  def test_15(self):
    ''' two rectangles with exact overlap
    '''
    #up = Rectangle(coordinates=(0, 6), dim=(3, 3))
    count, d = self.f.overlayTwoCells(
      Rectangle(coordinates=(0, 0), dim=(3, 3)),
      Rectangle(coordinates=(0, 0), dim=(3, 3))
    )
    self.assertEqual(1, count)
    self.assertEqual('N', d)

  def test_16(self):
    ''' Rectangle with exact fit against a Parabola HACK
    '''
    expect = 0
    count, d = self.f.overlayTwoCells(
      Rectangle(coordinates=(20, 10), dim=(50, 10)),
      Parabola(
        coordinates=(0, 0), 
        edges={'a':10,'b':None,'c':10,'d':20}, 
        dim=(30, 30), direction='E'
      )
    )
    self.assertEqual(expect, count)

  #############
  # Gnomons   #
  #############
  def test_20(self):
    ''' generate two gnomons from an embedded square
    '''
    count = 4
    expect_g1 = ([1,1,5,5,2,2,1],[1,5,5,4,4,1,1])
    expect_g2 = ([2,2,4,4,5,5,2],[1,2,2,4,4,1,1])
    lower = Rectangle(coordinates=(1,1), dim=(4,4))
    upper = Rectangle(coordinates=(2,2), dim=(2,2))
    shapes = self.f.splitLowerUpper(count, lower, upper)
    self.assertEqual(expect_g1, shapes[0].xyPoints())
    self.assertEqual(expect_g2, shapes[1].xyPoints())
  def test_21(self):
    ''' north west gnomon meander 
    starting with lo (1,1) (4,4) and up (2,2) (2,2) 
    and after lo has been split from up to define centre coordinate
    '''
    expect = ([1, 1, 2, 2, 3, 3, 4, 4, 5, 5], [1, 5, 5, 4, 4, 5, 5, 4, 4, 5])
    g = Gnomon(coordinates=(1,1), edges={'a':2,'b':50000,'d':None,'c':4}, dim=(4,4))
    #g.printPoints()
    g.meander()
    self.assertEqual(g.xyPoints(), expect)
  def test_22(self):
    ''' south east gnomon meander
    '''
    #expect = ([2,2,3,3,4,4,5,5], [1,2,2,1,1,4,4,1])
    expect = ([2, 5, 5, 4, 4, 5, 5, 4], [1, 1, 2, 2, 3, 3, 4, 4])
    #g = Gnomon(coordinates=(2,1), edges={'a':2,'b':4,'c':2,'d':4}, dim=(3,3), direction='SE')
    g = Gnomon(coordinates=(2,1), edges={'a':2,'b':4,'c':4,'d':2}, dim=(3,3), direction='SE')
    g.meander()
    self.assertEqual(g.xyPoints(), expect)
   ###########
  # Parabolas #
   ###########
  def test_30(self):
    ''' parabola meander with direction=W
    '''
    expect = ([7,1,1,7,7,1,1,5,5,1,1,7,7,1], [1,1,2,2,3,3,4,4,5,5,6,6,7,7])
    p = Parabola(coordinates=(1,1), edges={'a':None,'b':5,'c':5,'d':3}, dim=(6,6), direction='W')
    p.meander()
    #p.printPoints()
    self.assertEqual(p.xyPoints(), expect)
  def test_31(self):
    ''' parabola south after split
    '''
    expect = ([1,1,3,3,5,5,7,7,1], [1,4,4,2,2,4,4,1,1])
    lo = Rectangle(coordinates=(1, 1), dim=(6, 3))
    up = Rectangle(coordinates=(3, 2), dim=(2, 3))
    numof_edges, d = self.f.overlayTwoCells(lo, up)
    shapes = self.f.splitLowerUpper(numof_edges, lo, up, direction=d)
    self.assertEqual(shapes[0].xyPoints(), expect)
  def test_32(self):
    ''' west
    '''
    expect = ([0,0,3,3,2,2,3,3,0], [0,3,3,2,2,1,1,0,0])
    lo = Rectangle(coordinates=(0, 0), dim=(3, 3))
    up = Rectangle(coordinates=(2, 1), dim=(3, 1))
    numof_edges, d = self.f.overlayTwoCells(lo, up)
    shapes = self.f.splitLowerUpper(numof_edges, lo, up, direction=d)
    self.assertEqual(shapes[0].xyPoints(), expect)
  def test_33(self):
    ''' north 
    '''
    expect = ([1,1,7,7,5,5,3,3,1], [1,3,3,1,1,2,2,1,1])
    lo = Rectangle(coordinates=(1, 1), dim=(6, 2))
    up = Rectangle(coordinates=(3, 0), dim=(2, 2))
    numof_edges, d = self.f.overlayTwoCells(lo, up)
    shapes = self.f.splitLowerUpper(numof_edges, lo, up, direction=d)
    self.assertEqual(shapes[0].xyPoints(), expect)
  def test_34(self):
    ''' east
    '''
    expect = ([1,1,2,2,1,1,4,4,1], [0,1,1,2,2,3,3,0,0])
    lo = Rectangle(coordinates=(1, 0), dim=(3, 3))
    up = Rectangle(coordinates=(0, 1), dim=(2, 1))
    numof_edges, d = self.f.overlayTwoCells(lo, up)
    shapes = self.f.splitLowerUpper(numof_edges, lo, up, direction=d)
    #shapes[0].printPoints()
    self.assertEqual(shapes[0].xyPoints(), expect)
  
  def test_35(self):
    ''' Labels help testers Yay!
    '''
    r = Rectangle((0, 0), (30,30), pencolor='CCC')
    '''
    self.assertEqual(r.label, 'RCCC     0  0 30 30')
    e = {'a':200,'b':401,'d':None,'c':400}
    g = Gnomon((100,100), (300,300), edges=e, pencolor='9ACD32')
    self.assertEqual(g.label, 'G9ACD32100100300300')
    '''

'''
the
end
'''
