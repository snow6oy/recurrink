''' cd ~/code/recurrink
    source v/bin/activate
    screen -S rink
    python -m unittest t.Test.test_n
'''
import unittest
import pprint
from flatten import Rectangle, Flatten, Parabola
pp = pprint.PrettyPrinter(indent=2)

### topdown use cases for Minkscape

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
    ''' done after first pass
    '''
    self.done = [
      Rectangle(pencolor='FFF', x=2, y=1, w=5, h=1), 
      Rectangle(x=1, y=1, w=1, h=1), 
      Rectangle(x=7, y=1, w=1, h=1)
    ]
    ''' list of rects todo
    '''
    # pos     size     color
    data = [
      [(0, 0, 3, 3), 'CCC'], # seeker 1
      [(3, 0, 3, 3), 'CCC'], # 3
      [(6, 0, 3, 3), 'CCC'], # seeker 2
      [(0, 0, 3, 3), 'FFF'],
      [(4, 0, 1, 3), '000'], # seeker 0
      [(7, 1, 1, 1), '000'],
      [(1, 1, 1, 1), '000'],
      [(2, 1, 5, 1), 'FFF'] 
    ]
    self.todo = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(data)
    ]
    self.f = Flatten()

  def test_1(self):
    ''' simple label check
    '''
    r = Rectangle(pencolor='000', x=10, y=10, w=10, h=10)
    self.assertEqual(r.label, 'R000    10 10 20 20')

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
        done.plotPoints(seeker=shapes[1], fn='topdown_3')

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
        done.plotPoints(seeker=shapes[0], fn='topdown_4')

  def test_6(self):
    ''' minkscape top 20 10 50 10 and seeker 0
    '''
    expect = [
      [[4, 4, 5, 5, 4], [2, 3, 3, 2, 2]], # N split
      [[4, 4, 5, 5, 4], [0, 1, 1, 0, 0]]  # S split
    ]
    label = [ 'R000     4  2  5  3', 'R000     4  0  5  1' ]
    done = Rectangle(x=2, y=1, w=5, h=1)
    done.plotPoints(seeker=self.seeker[1], fn='topdown_6a')
    shapes = self.f.overlayTwoCells(self.seeker[0], done)
    done.plotPoints(seeker=shapes[0], fn='topdown_6b')
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
      self.assertTrue(len(shapes)) # fail on purpose

  def test_8(self):
    ''' this proves that Flatten.overlayTwoCell is required
        which is a problem because we have Parabolas at this stage
    '''
    r1 = Rectangle(x=3,y=0,w=3,h=1)
    r2 = Rectangle(x=4,y=0,w=1,h=1)
    shape = self.f.split(r1, r2, required=[{'R':'W'}, {'R':'E'}])
    self.assertEqual(shape[0].label, 'R000     3  0  4  1')
    self.assertEqual(shape[1].label, 'R000     5  0  6  1')

  def test_9(self):
    ''' Rectangle.set_seeker when splitting long rectangle into cubes 
        called by Flatten.split
    '''
    seeker = Rectangle(x=4, y=0, w=1, h=3)
    done   = Rectangle(x=1, y=1, w=7, h=1) # copy of done
    done.set_seeker(seeker, 'S')           # transform done copy into seeker
    done.plotPoints(seeker=seeker, fn='topdown_9')
    x, y, w, h = done.dimensions()   # get the new values
    done.set_dimensions({'x':x, 'y':y, 'w':w, 'h':h}, direction='S', pencolor=seeker.pencolor) # apply for meander
    done.meander()
    xy = list(done.linefill.coords)
    print(f"{done.label=} {done.box.bounds=} {done.direction=}")
    pp.pprint(xy)

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
    self.f.firstPass(self.todo) # create Flatten().done
    self.assertTrue(len(self.f.todo))
    todo = [x for x in self.f.todo]  # make a hard copy
    invisibles = self.f.expungeInvisibles(todo)
    # print(len(invisibles))
    self.assertEqual(len(invisibles), 1)
    # self.f.todo = [x for x in f.todo if x not in invisibles] # omit the invisibles

  def test_12(self):
    ''' stage three: Merge Them Whats Done
    '''
    count = len(self.done)
    self.f.mergeDone(self.done)     # should set two merged Polygons in Flatten
    if count > len(self.f.merge_d): # if something merged then check again
      done = self.f.merge_d[:]      # hard copy
      self.f.merge_d = []      
      self.f.mergeDone(done)        # compare two merged Polygons with each other
      #[print(p.box.bounds) for p in self.f.merge_d]
    p1 = self.f.merge_d[0]
    #print(p1.label)
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
    self.f.merge_d = [r]              # assign to Flatten to crop against
    todo = [t for t in self.todo if t.label not in already_done]
    cropped = self.f.cropSeekers(todo)
    #[print(crop.label) for crop in cropped]
    for c in cropped:
      if c.label in ['R000     4  2  5  3','R000     4  0  5  1']:
        print(f"{c.label=} {c.box.bounds=} {c.direction=}")

    #[self.assertEqual(crop.label, expect[i]) for i, crop in enumerate(cropped)]

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
    pfff = Parabola(Rectangle(pencolor='FFF', x=0,y=0,w=3,h=3), Rectangle(x=1,y=1,w=2,h=1), direction='W')
    pccc = Parabola(Rectangle(pencolor='CCC', x=6,y=0,w=3,h=3), Rectangle(x=6,y=1,w=2,h=1), direction='E')
    seekers = [
      pfff,
      pccc,
      Rectangle(x=4, y=2, w=1, h=1),
      Rectangle(x=4, y=0, w=1, h=1),
      Rectangle(pencolor='CCC', x=3, y=2, w=3, h=1),
      Rectangle(pencolor='CCC', x=3, y=0, w=3, h=1)
    ]
    # now we have simulated what stage five gave us .. 
    to_compare = seekers[:]
    self.f.cmpSeekers(to_compare) # any compared that overlap are saved in Flatten.found
    # almost there
    new_seekers = self.f.assemble(seekers)
    c = new_seekers[2] # 4253
    c.meander()
    xy = list(c.linefill.coords)
    print(f"{c.label=} {c.box.bounds=} {c.direction=}")
    pp.pprint(xy)
    new_seekers.extend(self.done) # not the folk singers :-)
    [print(s.label) for s in new_seekers]
    #[print(ns) for ns in self.f.found.keys()]
    [self.assertEqual(ns.label, expect[i]) for i, ns in enumerate(new_seekers)]

'''
the
end
'''
