''' cd ~/code/recurrink
    source v/bin/activate
    screen -S rink
    python -m unittest t.Test.test_n
'''
import unittest
import pprint
from flatten import Rectangle, Flatten
pp = pprint.PrettyPrinter(indent=2)

### topdown use cases 

class Test(unittest.TestCase):
  def setUp(self):
    self.f = Flatten()
    self.seeker = [
      Rectangle(x=4, y=0, w=1, h=3),
      Rectangle(x=0, y=0, w=3, h=3),
      Rectangle(x=6, y=0, w=3, h=3),
      Rectangle(x=3, y=0, w=3, h=3)
    ]

  def test_1(self):
    ''' minkscape top cell 10 10 10 10
        s1 [] s2 gnomons *2 s3 [] s4 []
    '''
    expect = [ None, ['G000     0  0  3  3','G000     1  0  3  2'], None, None ]
    done = Rectangle(x=1,y=1,w=1,h=1)
    #done.plotPoints(seeker=self.seeker[1], fn='topdown_2')
    for i, e in enumerate(expect):
      shapes = self.f.overlayTwoCells(self.seeker[i], done)
      if len(shapes) == 0:
        self.assertFalse(expect[i])
      else:
        [self.assertTrue(s.label in expect[i]) for s in shapes]
        done.plotPoints(seeker=shapes[1], fn='topdown_1')

  def test_2(self):
    ''' minkscape top cell 70 10 10 10
    '''
    expect = [ None, None, ['G000     6  0  9  3','G000     7  0  9  2'], None ]
    done = Rectangle(x=7, y=1, w=1, h=1)
    #done.plotPoints(seeker=self.seeker[2], fn='topdown_3')
    for i, e in enumerate(expect):
      shapes = self.f.overlayTwoCells(self.seeker[i], done)
      if len(shapes) == 0:
        self.assertFalse(expect[i])
      else:
        [self.assertTrue(s.label in expect[i]) for s in shapes]
        done.plotPoints(seeker=shapes[0], fn='topdown_2')

  def test_3(self):
    ''' minkscape top 20 10 50 10 and seeker 0
    '''
    expect = [
      [[4, 4, 5, 5, 4], [2, 3, 3, 2, 2]], # N split
      [[4, 4, 5, 5, 4], [0, 1, 1, 0, 0]]  # S split
    ]
    label = [ 'R000     4  2  5  3', 'R000     4  0  5  1' ]
    done = Rectangle(x=2, y=1, w=5, h=1)
    shapes = self.f.overlayTwoCells(self.seeker[0], done)
    done.plotPoints(seeker=shapes[0], fn='topdown_3')
    for i in range(2):
      #print(label[i])
      self.assertEqual(shapes[i].label, label[i])
      xy = shapes[i].boundary.xy
      #pp.pprint(xy[0].tolist())
      #pp.pprint(expect[i][0])
      self.assertEqual(xy[0].tolist(), expect[i][0])
      self.assertEqual(xy[1].tolist(), expect[i][1])

  def test_4(self):
    ''' minkscape top 20 10 50 10 and seeker 1
    '''
    done = Rectangle(x=2, y=1, w=5, h=1)
    shapes = self.f.overlayTwoCells(self.seeker[1], done)
    if len(shapes):
      done.plotPoints(seeker=shapes[0], fn='topdown_4')
      # TODO pencolor is not 000
      self.assertEqual(shapes[0].label, 'P000     0  0  3  3')

  def test_5(self):
    ''' minkscape top 20 10 50 10 and seeker 2 after splitting
    '''
    done = Rectangle(x=2, y=1, w=5, h=1)
    #done.plotPoints(seeker=self.seeker[2], fn='topdown_5')
    shapes = self.f.overlayTwoCells(self.seeker[2], done)
    if len(shapes):
      done.plotPoints(seeker=shapes[0], fn='topdown_5')
      self.assertEqual(shapes[0].label, 'P000     6  0  9  3')
    else:
      self.assertTrue(len(shapes)) 

  def test_6(self):
    ''' minkscape top 20 10 50 10 and seeker 3
    '''
    expect = [
      [[4, 4, 5, 5, 4], [2, 3, 3, 2, 2]], # N split
      [[4, 4, 5, 5, 4], [0, 1, 1, 0, 0]]  # S split
    ]
    label = [ 'R000     4  2  5  3', 'R000     4  0  5  1' ]
    done = Rectangle(x=2, y=1, w=5, h=1)
    #done.plotPoints(seeker=self.seeker[3], fn='topdown_6')
    shapes = self.f.overlayTwoCells(self.seeker[3], done)
    if len(shapes):
      done.plotPoints(seeker=shapes[1], fn='topdown_6') # S seeker
      self.assertEqual(shapes[0].label, 'R000     3  2  6  3')
      self.assertEqual(shapes[1].label, 'R000     3  0  6  1')
    else:
      self.assertTrue(len(shapes)) # fail on purpose
'''
the
end
'''
