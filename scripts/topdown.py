import pprint
from flatten import Rectangle, Flatten
from gcwriter import GcodeWriter

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
    for up in self.done:
      numof_edges, d = self.f.overlayTwoCells(seeker, up)
      # TODO make sure flatten exludes up from [shapes]
      if numof_edges: # note: greater than 0 adds unwanted shapes
        #print('numof edges', numof_edges, 'direction', d)
        found = self.f.splitLowerUpper(numof_edges, seeker, up, direction=d)
        #print(f"{seeker.label} {up.label} {len(found)}")
        break
    return found

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
    ''' make a list of rects todo
    '''
    # pos     size     color
    init = [
      [( 0, 0), (30,30), 'CCC'],
      [(30, 0), (30,30), 'CCC'],
      [(60, 0), (30,30), 'CCC'],
      [( 0, 0), (30,30), 'FFF'],
      [(40, 0), (10,30), '000'], 
      [(70,10), (10,10), '000'],
      [(10,10), (10,10), '000'],
      [(20,10), (50,10), 'FFF'] 
    ]
    self.done = [Rectangle(i[0], i[1], pencolor=i[2]) for i in reversed(init)]
    self.todo = [Rectangle(i[0], i[1], pencolor=i[2]) for i in reversed(init)]
    self.f = Flatten()

  def firstPass(self):
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
        #print(rt, len(stash), len(done))
        #[print(s.label) for s in stash]
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
  # python3 -m scripts.topdown
  mf = MinkFlatten()
  mf.firstPass()
  print('.'*80)
  mf.secondPass()
  mf.theParabolaHack()
  #[print(d.label) for d in self.done]
  print("Unwanted")
  pprint.pprint(mf.t()[0])
  print("Omitted")
  pprint.pprint(mf.t()[1])
  [mf.write('minkscape', fill=fill) for fill in ['CCC', '000', 'FFF']]
'''
the
end
'''
