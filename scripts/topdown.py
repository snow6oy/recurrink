import pprint
from flatten import Rectangle, Flatten
from gcwriter import GcodeWriter

''' Strategy is Top-N-Tail
    =collect the immutables aka top
    start with empty list done
    iterate through todo and add seeker to done 
    unless seeker overlaps with already done

    remove the invisibles aka background
    split remainder against immutables
    split remainder against themselves
    calculate sum of area to validate results
'''

class MinkFlatten():
  ''' tactical flattener that only knows Minkscape
  '''

  def findSpace(self, seeker):
    ''' attempt to find a space sought by this shape
    split any that collide and retest
    returning False will cause a rect to be ignored
    '''
    found = []
    #print(seeker.label)
    for d in self.done:
      found = self.f.overlayTwoCells(seeker, d)
      # TODO make sure flatten exludes up from [shapes]
      if len(found): # note: greater than 0 adds unwanted shapes
        #print('numof found ', len(found), 'direction', d)
        #print(f"s {seeker.label} d {d.label} {len(found)}")
        break
    return found

  def firstPass(self):
    ''' first pass 
        add any shape that does not collide with another
        these are immutable (cannot be split) and similar to "top cells"
    '''
    done = [] # if it works then remove from init
    for x in self.todo:
      for d in done:
        if self.f.overlapTwoCells(x, d):
          break
      else:
        done.append(x)
    self.todo = [t for t in self.todo if t not in done]
    self.done = done

  def findInvisibles(self, todo):
    invisibles = []
    x = todo.pop()
    for y in todo:
      if self.f.sameBoxen(x, y):
        # print(x.label, y.label)
        invisibles.append(x)
    if len(todo):
      self.findInvisibles(todo)
    return invisibles

  def _firstPass(self):
    ''' first pass 
        add any shape that does not collide with another
        these are immutable (cannot be split) and similar to "top cells"
    '''
    top = []
    for x in self.done:
      shapes = self.findSpace(x)
      if len(shapes) == 0:
        top.append(x)
    self.done = top
    self.todo = [t for t in self.todo if t not in top]


  def theParabolaHack(self):
    ''' parabolas cannot be added to done 
    because of a fault in collision detection
    this hack forces but only works for minkscape
    '''
    missing = ['PFFF     0  0 30 30', 'PCCC    60  0 30 30']
    for t in self.todo:
      for label in missing:
        if label == t.label:
          self.done.append(t) 

  # TODO look into Shapely.area()
  def checkAreaSum(expected_area, done=list()):
    ''' check the done set() by calculating the bounded area
    the sum of all bounded area should equal blocksize * cellsize
    if higher than fail because there are overlaps
    if lower then warn about unallocated whitespace (run visual check)
    '''
    area = 0
    for s in done:
      print(s.label, area)
      area += s.area()           # TODO Gnomon and Parabole area()
    if area > expected_area:
      #raise ValueError(f"overlapping: expected {expected_area} actual {area}")
      print(f"overlapping: expected {expected_area} actual {area}")
    elif area < expected_area:
      print(f"whitespace warning: expected {expected_area} actual {area}")

  def t(self):
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
    return unwanted, omitted

  def __init__(self):
    ''' make two lists of rects, todo and done, as exact copies
    '''
    # pos     size     color
    init = [
      [( 0, 0, 30,30), 'CCC'],
      [(30, 0, 30,30), 'CCC'],
      [(60, 0, 30,30), 'CCC'],
      [( 0, 0, 30,30), 'FFF'],
      [(40, 0, 10,30), '000'], 
      [(70,10, 10,10), '000'],
      [(10,10, 10,10), '000'],
      [(20,10, 50,10), 'FFF'] 
    ]
    '''
    self.done = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(init)
    ]
    '''
    self.todo = [
      Rectangle(pencolor=i[1], x=i[0][0], y=i[0][1], w=i[0][2], h=i[0][3]) for i in reversed(init)
    ]
    self.f = Flatten()

  def secondPass(self):
    ''' second pass
    compare the remaining shapes to top 
    shapes that collide are split and added for a subsequent retry
    or without colliding they are added directly
    further splitting may happen on subsequent retries
    but if there none then loop exists before max retries is reached
    '''
    retries = 3

    for rt in range(retries):
      stash = []
      for shape in self.todo:
        collides = self.findSpace(shape)
        if len(collides):
          [stash.append(c) for c in collides]
        else:
          self.done.append(shape)
        print(rt, len(stash), len(self.done))
        [print(s.label) for s in stash]
      else: # retry while there is stuff todo
        self.todo = stash
        #[print(t.label) for t in todo]
        continue

  def write(self, model, fill=None):
    ''' stream path data to file as gcodes
    '''
    gcw = GcodeWriter()
    fn = f'/tmp/{model}_{fill}.gcode'
    gcw.writer(fn)
    gcw.start()
    for s in self.done:
      #print(s.pencolor, fill)
      if s.pencolor == fill:
        #print(f"{s.label} {s.direction:<2}")
        s.meander()
        gcw.points(list(s.path))
    gcw.stop()
    return fn

if __name__ == '__main__':
  # python -m scripts.topdown
  #i = [(0,0,30,30), 'CCC']
  r = Rectangle(pencolor='000', x=10, y=10, w=10, h=10)
  print('ok1') if (r.label == 'R000    10 10 20 20') else print(r.label)
  mf = MinkFlatten()
  #shapes = mf.findSpace(r)
  #print('ok2') if len(shapes) == 2 else print('empty shape')
  #print('ok2') if (shapes[0].name == 'G') else print(shapes[0].name)
  mf.firstPass()
  top = ['R000    70 10 80 20', 'R000    10 10 20 20', 'RFFF    20 10 70 20']
  done_labels = [d.label for d in mf.done]
  for d in mf.done: # test for the 3 top cells 
    print('ok3') if d.label in top else print(d.label)
  print(len(mf.todo))
  print('.'*80)
  todo = [x for x in mf.todo]  # make a hard copy
  invisibles = mf.findInvisibles(todo)
  print(len(invisibles))
  mf.todo = [x for x in mf.todo if x not in invisibles]
  print(len(mf.todo))
  #mf.secondPass()
  [print(d.label) for d in mf.done]
  print('.'*80)
  [print(t.label) for t in mf.todo]
  '''
  print(a)
  #mf.theParabolaHack()
  print("Unwanted")
  pprint.pprint(mf.t()[0])
  print("Oh-mitted")
  pprint.pprint(mf.t()[1])
  [mf.write('minkscape', fill=fill) for fill in ['CCC', '000', 'FFF']]
  '''
'''
the
end
'''
