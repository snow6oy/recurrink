import unittest
import pprint
from shapely.geometry import Polygon
from shapes import Geomink, Plotter
from flatten import Flatten
#from fl8n import Flatten
pp = pprint.PrettyPrinter(indent=2)

# topdown use cases for Minkscape

class Test(unittest.TestCase):

  def setUp(self):
    pass

  def setUp(self):
    self.todo = [
      Geomink(pencolor='FFF', xywh=(2, 1, 7, 2)),
      Geomink(pencolor='000', xywh=(1, 1, 2, 2)),
      Geomink(pencolor='000', xywh=(7, 1, 8, 2)),
      Geomink(pencolor='000', xywh=(4, 0, 5, 3)), 
      Geomink(pencolor='FFF', xywh=(0, 0, 3, 3)),
      Geomink(pencolor='CCC', xywh=(6, 0, 9, 3)),
      Geomink(pencolor='CCC', xywh=(3, 0, 6, 3)),
      Geomink(pencolor='CCC', xywh=(0, 0, 3, 3)) 
    ]
    self.f = Flatten()
    self.writer = Plotter()

  def tearDown(self):
    ''' reset stencil
    print(len(self.f.stencil.geoms))
    '''
    self.f = Flatten()

  def test_1(self):
    ''' minkscape top 20 10 50 10 splits a seeker into a Parabola
    '''
    done   = self.todo[0]
    seeker = self.todo[5]
    self.f.add(done)
    self.f.run([seeker])
    self.assertTrue('P1' in self.f.doneLabels())
    self.writer.plot(done.shape, seeker.shape, fn='flatten_1')
   
  def test_2(self):
    ''' minkscape top cell 10 10 10 10 makes a Rectangle and Square Ring
    '''
    expect = ['R1','S1']
    done   = self.todo[1]
    seeker = self.todo[7]
    self.f.run([done, seeker])
    self.writer.plot(done.shape, seeker.shape, fn='flatten_2')
    self.assertTrue(len(self.f.done))
    [self.assertEqual(label, expect[i]) for i, label in enumerate(self.f.doneLabels())]

  def test_3(self):
    ''' minkscape top 20 10 50 10 and seeker 3
    '''
    expect = [
      [[2, 2, 7, 7, 2], [1, 2, 2, 1, 1]], # N split
      [[4, 5, 5, 4, 4], [1, 1, 0, 0, 1]]  # S split
    ]
    elabel = ['R1', 'R2' ]
    done   = self.todo[0]
    seeker = self.todo[3]
    self.f.run([done, seeker])
    self.writer.plot(done.shape, seeker.shape, fn='flatten_3')
    labels = self.f.doneLabels()
    for i in range(2):
      self.assertEqual(labels[i], elabel[i])
      gmk = self.f.get(labels[i])
      xy = gmk.shape.boundary.xy
      self.assertEqual(xy[0].tolist(), expect[i][0])
      self.assertEqual(xy[1].tolist(), expect[i][1])

  def test_4(self):
    ''' minkscape top 20 10 50 10 and seeker 7
    '''
    done   = self.todo[0]
    seeker = self.todo[7]
    self.f.run([done, seeker])
    self.writer.plot(done.shape, seeker.shape, fn='flatten_4')
    self.assertTrue(len(self.f.done))
    self.assertTrue('P1' in self.f.doneLabels())

  def test_5(self):
    ''' can Flatten.split handle seekers after cropping
    '''
    done   = Geomink(xywh=(3,0,6,1))
    seeker = Geomink(xywh=(4,0,5,1))
    self.writer.plot(done.shape, seeker.shape, fn='flatten_5')
    self.f.add(done)
    events = self.f.evalSeeker(seeker)
    self.assertFalse(events[0])

  def test_6(self):
    ''' when splitting into many rectangles check both were added
    '''
    self.f.run(self.todo[:3]) # merge three into one
    done     = self.f.stencil.geoms[0]
    seeker   = self.todo[3]
    covering = 2
    self.writer.plot(self.f.stencil.geoms[0], seeker.shape, fn='flatten_6')
    self.f.crop(seeker, [done])
    self.assertEqual(len(self.f.done), 5)

  def test_7(self):
    ''' expunge the invisibles
    self.writer.multiPlot(self.f.stencil, 'flatten_7')
    self.writer.plot(self.f.stencil.geoms[0], seeker.shape, fn='flatten_7')
    ''' 
    self.f.run(self.todo[:5]) # merge four into one stencil
    self.assertEqual(len(self.f.stencil.geoms), 1)
    seeker =  self.todo[-1]   # last shape is the invisible
    events = self.f.evalSeeker(seeker)
    '''
    self.assertEqual(events[0], 2)
    need to review this. the stencil is incorrect and 2 is not the correct control
    '''

  def test_8(self):
    ''' run statistics 
    print(self.f.stats)
    '''
    add    = 5
    merge  = 0
    crop   = 4
    ignore = 0
    punch  = 0

    self.f.run(self.todo)
    self.assertEqual(self.f.stats[0], add)
    self.assertEqual(self.f.stats[1], merge)
    self.assertEqual(self.f.stats[2], crop)
    self.assertEqual(self.f.stats[3], ignore)
    self.assertEqual(self.f.stats[4], punch)

  def test_9(self):
    ''' rectangle
    '''
    r     = Polygon([(1, 1), (1, 2), (2, 2), (2, 1)])
    gmk   = Geomink(polygon=r, label='R1')
    shape = self.f.shapeTeller(gmk.shape, 'rectangle')
    self.assertTrue(shape)

  def test_10(self):
    ''' gnomon
    '''
    g = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0)])
    gmk   = Geomink(polygon=g, label='G1')
    shape = self.f.shapeTeller(gmk.shape, 'gnomon')
    self.assertTrue(shape)

  def test_11(self):
    ''' parabola
    '''
    pb = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 1), (3, 1), (3, 0)])
    gmk   = Geomink(polygon=pb, label='P1')
    shape = self.f.shapeTeller(gmk.shape, 'parabola')
    self.assertTrue(shape)

  def test_12(self):
    ''' square ring
    '''
    hole  = [(1, 1), (1, 2), (2, 2), (2, 1)]
    outer = [(0, 0), (0, 3), (3, 3), (3, 0)]
    sr    = Polygon(outer, holes=[hole])
    gmk   = Geomink(polygon=sr, label='S1')
    shape = self.f.shapeTeller(gmk.shape, 'sqring')
    self.assertTrue(shape)

  def test_13(self):
    ''' dangling extra points
        when shapely operations leave dangling points simplify MIGHT tidy up, e.g.

        clean = polygon.boundary.simplify(tolerance=1)

        but it has unacceptable side-effect of clobbering Gnomons and Parabolas
        this test documents the risk of shapeTeller being fooled by the danglers
    '''
    r     = Polygon([(0, 0), (0, 1), (0, 3), (3, 3), (3, 0)])
    self.assertRaises(ValueError, Geomink, polygon=r)

  def test_14(self):
    ''' with many polys in stencil multiple touches are possible
    p1     = Polygon([(1, 1), (1, 9), (9, 9), (9, 1)])
    seeker = Geomink(polygon=p1, label='R1')
    p2     = Polygon([(9, 1), (9, 9), (17, 9), (17, 1)])
    done1  = Geomink(polygon=p2, label='R2')
    p3     = Polygon([(1, 9), (1, 17), (9, 17), (9, 9)])
    done2  = Geomink(polygon=p3, label='R3')
    self.f.add(done1)
    self.f.add(done2)
    self.f.run([seeker])
    self.writer.plot(self.f.stencil.geoms[0], seeker.shape, fn='flatten_14')
    '''

  def test_15(self):
    ''' add first shape to an empty stencil
    '''
    ev = self.f.evalSeeker(self.todo)
    self.assertTrue(ev[0])  # returns 1

  def test_16(self):
    ''' add shape that touches
    '''
    self.f.add(self.todo[4])
    ev = self.f.evalSeeker(self.todo[6])
    self.assertEqual(ev[1].bounds, (0.0, 0.0, 3.0, 3.0))

  def test_17(self):
    ''' ignore covering shape
    '''
    self.f.add(self.todo[4])
    ev = self.f.evalSeeker(self.todo[4])
    self.assertFalse(ev[0])  # returns 0

  def test_18(self):
    ''' crop event
    '''
    self.f.add(self.todo[0])
    ev = self.f.evalSeeker(self.todo[3])
    self.assertEqual(ev[0], 2)
    self.assertEqual(ev[1].bounds, (2.0, 1.0, 7.0, 2.0))

  def test_19(self):
    ''' punch  event
    '''
    self.f.add(self.todo[2])
    ev = self.f.evalSeeker(self.todo[5])
    self.assertEqual(ev[0], 3)
    self.assertEqual(ev[1].bounds, (7.0, 1.0, 8.0, 2.0))

  def test_20(self):
    ''' add with multi touch
    self.writer.plot(self.f.stencil.geoms[0], self.todo[6].shape, fn='flatten_17')
    '''
    self.f.add(self.todo[5])
    self.f.add(self.todo[7])
    ev = self.f.evalSeeker(self.todo[6])
    control = ev.pop(0)
    self.assertTrue(control)       # expect 1
    self.assertEqual(len(ev), 1)   # two remaining

  def test_21(self):
    ''' add seeker can tell when add succeeded
    '''
    self.todo[0].label = 'R'  # normally done by Flatten.identify()
    ok = self.f.addSeeker(self.todo[0])
    self.assertTrue(ok)
    not_ok = self.f.addSeeker(self.todo[0])
    self.assertFalse(not_ok)

'''
the
end
'''
