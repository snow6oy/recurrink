''' cd ~/code/recurrink
    source v/bin/activate
    screen -S rink
    python -m unittest t.Test.test_n
'''
import unittest
import pprint
from shapes import Rectangle, Parabola
from flatten import Flatten
pp = pprint.PrettyPrinter(indent=2)

### topdown use cases for Minkscape

class Test(unittest.TestCase):
  def setUp(self):
    self.todo = [
      Rectangle(pencolor='FFF', x=2, y=1, w=5, h=1),
      Rectangle(pencolor='000', x=1, y=1, w=1, h=1),
      Rectangle(pencolor='000', x=7, y=1, w=1, h=1),
      Rectangle(pencolor='000', x=4, y=0, w=1, h=3), # s0
      Rectangle(pencolor='FFF', x=0, y=0, w=3, h=3),
      Rectangle(pencolor='CCC', x=6, y=0, w=3, h=3), # s2
      Rectangle(pencolor='CCC', x=3, y=0, w=3, h=3), # s3
      Rectangle(pencolor='CCC', x=0, y=0, w=3, h=3)  # s1
    ]
    self.f = Flatten()

  def test_1(self):
    ''' minkscape top 20 10 50 10 splits a seeker into a Parabola
    '''
    done   = self.todo[0]
    seeker = self.todo[5]
    shapes = self.f.overlayTwoCells(seeker, done)
    if len(shapes):
      done.plotPoints(seeker=shapes[0], fn='flatten_1')
      self.assertEqual(shapes[0].label, 'PCCC     6  0  9  3')
    else:
      self.assertTrue(len(shapes)) 

  def test_2(self):
    ''' minkscape top cell 10 10 10 10 makes Gnomons
    '''
    expect = ['GCCC     0  0  3  3','GCCC     1  0  3  2']
    done   = self.todo[1]
    seeker = self.todo[7]
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=seeker, fn='flatten_2')
    self.assertTrue(len(shapes))
    [self.assertTrue(s.label in expect) for s in shapes]

  def test_3(self):
    ''' minkscape top cell 70 10 10 10
    '''
    expect = ['GCCC     6  0  9  3','GCCC     7  0  9  2']
    done   = self.todo[2]
    seeker = self.todo[5]
    shapes = self.f.overlayTwoCells(seeker, done)
    done.plotPoints(seeker=seeker, fn='flatten_3')
    self.assertTrue(len(shapes))
    [self.assertTrue(s.label in expect) for s in shapes]

  def test_4(self):
    ''' minkscape top 20 10 50 10 and seeker 3
    '''
    expect = [
      [[4, 4, 5, 5, 4], [2, 3, 3, 2, 2]], # N split
      [[4, 4, 5, 5, 4], [0, 1, 1, 0, 0]]  # S split
    ]
    label = [ 'R000     4  2  5  3', 'R000     4  0  5  1' ]
    done   = self.todo[0]
    seeker = self.todo[3]
    done.plotPoints(seeker=seeker, fn='flatten_4')
    shapes = self.f.overlayTwoCells(seeker, done)
    for i in range(2):
      self.assertEqual(shapes[i].label, label[i])
      xy = shapes[i].boundary.xy
      self.assertEqual(xy[0].tolist(), expect[i][0])
      self.assertEqual(xy[1].tolist(), expect[i][1])

  def test_5(self):
    ''' minkscape top 20 10 50 10 and seeker 7
    '''
    done   = self.todo[0]
    seeker = self.todo[7]
    shapes = self.f.overlayTwoCells(seeker, done)
    self.assertTrue(len(shapes))
    done.plotPoints(seeker=shapes[0], fn='flatten_5')
    self.assertEqual(shapes[0].label, 'PCCC     0  0  3  3')

  def test_8(self):
    ''' can Flatten.split handle seekers after cropping
    '''
    r1 = Rectangle(x=3,y=0,w=3,h=1)
    r2 = Rectangle(x=4,y=0,w=1,h=1)
    #r1.plotPoints(seeker=r2, fn='flatten_8')
    shape = self.f.split(r1, r2, required=[{'R':'W'}, {'R':'E'}])
    self.assertEqual(shape[0].label, 'R000     3  0  4  1')
    self.assertEqual(shape[1].label, 'R000     5  0  6  1')

  def test_9(self):
    ''' Rectangle.setSeeker when splitting long rectangle into cubes 
    '''
    seeker  = self.todo[3]
    merge_d = Rectangle(x=1, y=1, w=7, h=1)  # copy of 3 dones merged
    merge_d.setSeeker(seeker, 'S')           # transform done copy into seeker
    x,y,w,h = merge_d.dimensions()   # get the new values
    # apply for meander
    merge_d.setDimensions({'x':x, 'y':y, 'w':w, 'h':h}, direction='S', pencolor=seeker.pencolor) 
    self.assertEqual(merge_d.box.bounds, (4, 0, 5, 1))
    '''
    print(f"{merge_d.label=} {merge_d.box.bounds=} {merge_d.direction=}")
    '''

  ##########################################
  def test_10(self):
    ''' stage one: gather the immutables
    '''
    expect = ['R000     7  1  8  2', 'R000     1  1  2  2', 'RFFF     2  1  7  2']
    self.f.firstPass(self.todo) # create Flatten().done
    [self.assertTrue(d.label in expect) for d in self.f.done] # test for the 3 top cells 

  def test_11(self):
    ''' stage two: expunge the invisibles
    ''' 
    self.test_10()         # prime Flatten.done with 3 tops
    todo = self.f.todo[:]  # make a hard copy
    invisibles = self.f.expungeInvisibles(todo)
    self.assertEqual(len(invisibles), 1)

  def test_12(self):
    ''' stage three: Merge Them Whats Done
    '''
    self.test_10()                  # prime Flatten.done with 3 tops
    done  = self.f.done[:]          # local copy
    count = len(done)
    self.f.mergeDone(done)          # should set two merged Polygons in Flatten
    if count > len(self.f.merge_d): # if something merged then check again
      done = self.f.merge_d[:]      # another local copy
      self.f.merge_d = []      
      self.f.mergeDone(done)        # compare two merged Polygons with each other
      #[print(p.box.bounds) for p in self.f.merge_d]
    p1 = self.f.merge_d[0]
    self.assertEqual(list(p1.box.bounds), [1, 1, 8, 2])

  def test_13(self):
    ''' stage four: crop seekers against the merged immutables
    '''
    expect = [
      'R000     4  2  5  3',
      'R000     4  0  5  1',
      'PFFF     0  0  3  3',
      'PCCC     6  0  9  3',
      'RCCC     3  2  6  3',
      'RCCC     3  0  6  1'
    ]
    already_done = [  # imitate removal of Immutables and Invisibles
      'RCCC     0  0  3  3', # invisible
      'R000     7  1  8  2', 
      'R000     1  1  2  2', 
      'RFFF     2  1  7  2'
    ]
    r = Rectangle(x=1,y=1,w=7,h=1) # merge all three done into one for spatial tests
    self.f.merge_d = [r]           # assign to Flatten to crop against
    todo = [t for t in self.todo if t.label not in already_done]
    cropped = self.f.cropSeekers(todo)
    [self.assertEqual(crop.label, expect[i]) for i, crop in enumerate(cropped)]

  def test_14(self):
    ''' final stage: compare the seekers against each other
    '''
    expect = [
      'PFFF     0  0  3  3',
      'PCCC     6  0  9  3',
      'R000     4  2  5  3',
      'R000     4  0  5  1',
      'RCCC     3  0  4  1',
      'RCCC     5  0  6  1',
      'RCCC     3  2  4  3',
      'RCCC     5  2  6  3',
      'RFFF     2  1  7  2',
      'R000     1  1  2  2',
      'R000     7  1  8  2'
    ]
    pfff = Parabola(
      Rectangle(pencolor='FFF', x=0,y=0,w=3,h=3), 
      Rectangle(x=1,y=1,w=2,h=1), 
      direction='W'
    )
    pccc = Parabola(
      Rectangle(pencolor='CCC', x=6,y=0,w=3,h=3), 
      Rectangle(x=6,y=1,w=2,h=1), 
      direction='E'
    )
    seekers = [
      pfff,
      pccc,
      Rectangle(x=4, y=2, w=1, h=1),
      Rectangle(x=4, y=0, w=1, h=1),
      Rectangle(pencolor='CCC', x=3, y=2, w=3, h=1),
      Rectangle(pencolor='CCC', x=3, y=0, w=3, h=1)
    ]
    self.test_10()                  # prime Flatten.done with 3 tops
    done  = self.f.done[:]          # local copy
    # now we have simulated what stage five gave us .. 
    to_compare = seekers[:]
    self.f.cmpSeekers(to_compare)   # any compared that overlap are saved in Flatten.found
    # almost there
    new_seekers = self.f.assemble(seekers)
    new_seekers.extend(done)        # not the folk singers :-)
    #[print(s.label) for s in new_seekers]
    [self.assertEqual(ns.label, expect[i]) for i, ns in enumerate(new_seekers)]
'''
the
end
'''
