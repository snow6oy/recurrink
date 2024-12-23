import unittest
import pprint
from shapes import Geomink  
from flatten import Flatten, Plotter
pp = pprint.PrettyPrinter(indent=2)

### topdown use cases for Minkscape

class Test(unittest.TestCase):
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

  def test_1(self):
    ''' minkscape top 20 10 50 10 splits a seeker into a Parabola
    '''
    done   = self.todo[0]
    seeker = self.todo[5]
    self.f.run([done, seeker])
    self.assertEqual(self.f.done[1].label, 'P1')
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
    [self.assertEqual(d.label, expect[i]) for i, d in enumerate(self.f.done)]

  def test_3(self):
    ''' minkscape top 20 10 50 10 and seeker 3
    '''
    expect = [
      [[2, 2, 7, 7, 2], [1, 2, 2, 1, 1]], # N split
      [[4, 5, 5, 4, 4], [1, 1, 0, 0, 1]]  # S split
    ]
    label = ['R1', 'R2' ]
    done   = self.todo[0]
    seeker = self.todo[3]
    self.f.run([done, seeker])
    self.writer.plot(done.shape, seeker.shape, fn='flatten_3')
    for i in range(2):
      self.assertEqual(self.f.done[i].label, label[i])
      xy = self.f.done[i].shape.boundary.xy
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
    self.assertEqual(self.f.done[1].label, 'P1')

  def test_5(self):
    ''' can Flatten.split handle seekers after cropping
    '''
    done   = Geomink(xywh=(3,0,6,1))
    seeker = Geomink(xywh=(4,0,5,1))
    self.writer.plot(done.shape, seeker.shape, fn='flatten_5')
    self.f.mpAppend(done.shape)
    covering, empty = self.f.evalSeeker(seeker)
    self.assertEqual(covering, 3)
    self.assertFalse(empty)

  def test_6(self):
    ''' when splitting into many rectangles check both were added
    '''
    self.f.run(self.todo[:3]) # merge three into one
    done     = self.f.stencil.geoms[0]
    seeker   = self.todo[3]
    covering = 2
    self.writer.plot(self.f.stencil.geoms[0], seeker.shape, fn='flatten_6')
    self.f.crop(seeker, done)
    self.assertEqual(len(self.f.done), 5)

  def test_7(self):
    ''' expunge the invisibles
    ''' 
    self.f.run(self.todo[:5]) # merge four into one stencil
    self.assertEqual(len(self.f.stencil.geoms), 1)
    seeker =  self.todo[-1]   # last shape is the invisible
    self.writer.plot(self.f.stencil.geoms[0], seeker.shape, fn='flatten_7')
    covering, shape = self.f.evalSeeker(seeker)
    self.assertEqual(covering, 3)
    self.assertFalse(shape)

  def test_8(self):
    ''' run statistics 
    '''
    add    = 1
    merge  = 2
    crop   = 4
    ignore = 1
    punch  = 0

    self.f.run(self.todo)
    #print(self.f.stats)
    self.assertEqual(self.f.stats[0], add)
    self.assertEqual(self.f.stats[1], merge)
    self.assertEqual(self.f.stats[2], crop)
    self.assertEqual(self.f.stats[3], ignore)
    self.assertEqual(self.f.stats[4], punch)

'''
the
end
'''
