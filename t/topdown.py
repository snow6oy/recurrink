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
    ''' seekers downscaled for matplotlib
    '''
    self.seeker = [
      Rectangle(x=4, y=0, w=1, h=3),
      Rectangle(x=0, y=0, w=3, h=3),
      Rectangle(x=6, y=0, w=3, h=3),
      Rectangle(x=3, y=0, w=3, h=3)
    ]
    # TODO units are 10 times too big
    ''' make lists of rects todo
    '''
    # pos     size     color
    data = [
      [( 0, 0, 30,30), 'CCC'], # seeker 1
      [(30, 0, 30,30), 'CCC'], # 3
      [(60, 0, 30,30), 'CCC'], # seeker 2
      [( 0, 0, 30,30), 'FFF'],
      [(40, 0, 10,30), '000'], # seeker 0
      [(70,10, 10,10), '000'],
      [(10,10, 10,10), '000'],
      [(20,10, 50,10), 'FFF'] 
    ]
    self.todo = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(data)
    ]
    self.f = Flatten()

  def test_1(self):
    ''' simple label check
    '''
    r = Rectangle(pencolor='000', x=10, y=10, w=10, h=10)
    #print(r.label)
    self.assertEqual(r.label, 'R000    10 10 20 20')

  def test_3(self):
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

  def test_4(self):
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

  def test_6(self):
    ''' minkscape top 20 10 50 10 and seeker 0
    '''
    expect = [
      [[4, 4, 5, 5, 4], [2, 3, 3, 2, 2]], # N split
      [[4, 4, 5, 5, 4], [0, 1, 1, 0, 0]]  # S split
    ]
    label = [ 'R000     4  2  5  3', 'R000     4  0  5  1' ]
    done = Rectangle(x=2, y=1, w=5, h=1)
    done.plotPoints(seeker=self.seeker[1], fn='topdown_3a')
    shapes = self.f.overlayTwoCells(self.seeker[0], done)
    done.plotPoints(seeker=shapes[0], fn='topdown_3b')
    for i in range(2):
      #print(label[i])
      self.assertEqual(shapes[i].label, label[i])
      xy = shapes[i].boundary.xy
      #pp.pprint(xy[0].tolist())
      #pp.pprint(expect[i][0])
      self.assertEqual(xy[0].tolist(), expect[i][0])
      self.assertEqual(xy[1].tolist(), expect[i][1])

  def test_5(self):
    ''' minkscape top 20 10 50 10 and seeker 1
    '''
    done = Rectangle(x=2, y=1, w=5, h=1)
    shapes = self.f.overlayTwoCells(self.seeker[1], done)
    if len(shapes):
      done.plotPoints(seeker=shapes[0], fn='topdown_4')
      # TODO pencolor is not 000
      self.assertEqual(shapes[0].label, 'P000     0  0  3  3')

  def test_2(self):
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

  def test_7(self):
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
      self.assertTrue(len(shapes)) # fail on purposeG

  def test_12(self):
    ''' final test using labels
    '''
    expected = [
      'PFFF     0  0 30 30',
      'RCCC    30 20 10 10',
      'R000    10 10 10 10',
      'R000    70 10 10 10',
      'RCCC    30  0 10 10',
      'RCCC    50  0 10 10',
      'RCCC    50 20 10 10',
      'R000    40  0 10 10',
      'R000    40 20 10 10',
      'PCCC    60  0 30 30',
      'RFFF    20 10 50 10' 
    ]
    unwanted = [x.label for x in self.done if x.label not in expected]
    done_labels = set([d.label for d in self.done])
    omitted = [e for e in expected if e not in done_labels]
    print("Unwanted")
    pprint.pprint(mf.t()[0])
    print("Oh-mitted")
    pprint.pprint(mf.t()[1])

  def test_8(self):
    ''' gather the immutables
    '''
    self.f.firstPass(self.todo) # create Flatten().done
    top = ['R000    70 10 80 20', 'R000    10 10 20 20', 'RFFF    20 10 70 20']
    for d in self.f.done: # test for the 3 top cells 
      self.assertTrue(d.label in top)

  def test_9(self):
    ''' expunge the invisibles
    ''' 
    self.f.firstPass(self.todo) # create Flatten().done
    self.assertTrue(len(self.f.todo))
    todo = [x for x in self.f.todo]  # make a hard copy
    invisibles = self.f.expungeInvisibles(todo)
    # print(len(invisibles))
    self.assertEqual(len(invisibles), 1)
    # self.f.todo = [x for x in f.todo if x not in invisibles] # omit the invisibles

  def test_10(self):
    ''' stage three: Crop The Seekers
    '''
    self.expect_cropped = [
      'R000    40 20 50 30',
      'R000    40  0 50 10',
      'PFFF     0  0 30 30',
      'PCCC    60  0 90 30',
      'RCCC    30 20 60 30',
      'RCCC    30  0 60 10',
      'GFFF     0  0 30 30',
      'GFFF    10  0 30 20',
      'GCCC    60  0 90 30',
      'GCCC    70  0 90 20'
    ]
    self.f.firstPass(self.todo) # create Flatten().done
    todo = self.f.todo # original todo but without done
    safe = [x for x in todo] # hard copy
    invisibles = self.f.expungeInvisibles(todo) # now todo is empty but safe still remembers
    todo = [x for x in safe if x not in invisibles] # excuse the invisibles
    #[print(t.label) for t in todo]
    self.assertEqual(len(todo), 4) 
    cropped = self.f.cropSeekers(todo)
    for i, c in enumerate(cropped):
      self.assertEqual(expect[i], c.label)

  def test_11(self):
    ''' try reverse order ? 
    '''
    # repeat test 10
    self.f.firstPass(self.todo) 
    todo = self.f.todo # original todo but without done
    safe = [x for x in todo] # hard copy
    invisibles = self.f.expungeInvisibles(todo) # now todo is empty but safe still remembers
    todo = [x for x in safe if x not in invisibles] # excuse the invisibles
    cropped = self.f.cropSeekers(todo)
    [print(d.label) for d in self.f.done]
    #[print(crop.label) for crop in cropped]
    print('^'*80)
    # now continue with stage four: Clean The Cropped
    cleaned = self.f.cleanCropped(cropped)  
    #[print(clean.label) for clean in cleaned]

  def test_13(self):
    ''' collision detection with gnomons 
    '''
    done_1 = Rectangle(x=1,y=1,w=1,h=1)
    done_2 = Rectangle(x=2,y=1,w=5,h=1)
    (gnomon_nw, gnomon_se) = self.f.overlayTwoCells(self.seeker[1], done_1)
    done_1.plotPoints(seeker=gnomon_nw, fn='topdown_13nw')
    done_2.plotPoints(seeker=gnomon_se, fn='topdown_13')
    print(self.f.overlapTwoCells(gnomon_nw, done_1))  # overlap TRUE cross FALSE intersect TRUE
    print()
    print(self.f.overlapTwoCells(gnomon_se, done_2))  # overlap TRUE cross FALSE intersect TRUE

'''
the
end
'''
