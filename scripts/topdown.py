from flatten import Rectangle, Flatten

def whitespace(this, retry=False):
  ''' attempt to find whitespace for this rectangle
  split any that collide and retest
  returning False will cause a rect to be ignored
  '''
  #print(this.label)
  found = True # have whitespace
  for up in done:
    numof_edges, d = f.overlayTwoCells(this, up)
    if numof_edges == 1:
      found = False # position already occupied
      break
    elif numof_edges > 1:
      #print('numof edges', numof_edges, 'direction', d)
      shapes = f.splitLowerUpper(numof_edges, this, up, direction=d)
      if len(shapes) and not retry:
        [collisions.add(s) for s in shapes]
        found = False # no more room in here
        break
  return found

def whitespaceAgain(this, retry=False):
  print(this.label)
  for up in done:
    numof_edges, d = f.overlayTwoCells(this, up)
    if numof_edges:
      print('numof edges', numof_edges, 'direction', d)
      shapes = f.splitLowerUpper(numof_edges, this, up, direction=d)
      print(len(shapes))
      [print(s.label) for s in shapes]
  return None

def oneRect(this):
  ''' if no collisions are detected move item to done
  '''
  r = Rectangle(coordinates=this[0], dim=this[1], pencolor=this[2])
  if whitespace(r):
    done.add(r)

def checkAreaSum(expected_area):
  ''' check the done set() by calculating the bounded area
  the sum of all bounded area should equal blocksize * cellsize
  if higher than fail because there are overlaps
  if lower then warn about unallocated whitespace (run visual check)
  '''
  area = 0
  for s in done:
    print(area, s.label)
    area += s.area()           # Gnomon and Parabole shapes are NOT done
  if area > expected_area:
    #raise ValueError(f"overlapping: expected {expected_area} actual {area}")
    print(f"overlapping: expected {expected_area} actual {area}")
  elif area < expected_area:
    print(f"whitespace warning: expected {expected_area} actual {area}")


''' make a list of rects todo
'''
todo = [
  # pos     size     color
  [( 0, 0), (30,30), 'CCC'],
  [(30, 0), (30,30), 'CCC'],
  [(60, 0), (30,30), 'CCC'],
  [( 0, 0), (30,30), 'FFF'],
  [(40, 0), (10,30), '000'], 
  [(70,10), (10,10), '000'],
  [(10,10), (10,10), '000'],
  [(20,10), (50,10), 'FFF'] 
]

''' create a done list to target the final rects
and a collissions bucket for the misses
'''
done = set()
collisions = set()
expected_area = 3 * 1 * 30 * 30 # blocksize * cellsize
f = Flatten()
''' reverse iterate through todo list, comparing against done
stop once the todo list is empty
'''
[oneRect(todo.pop()) for rect in todo[:]]
checkAreaSum(expected_area)
[done.add(c) for c in collisions if whitespace(c, retry=True)]
checkAreaSum(expected_area)


'''
tmp = set()
[tmp.add(c) for c in collisions]
collisions.clear()
'''

print("remainder from collisions, copied to tmp")
for c in collisions:
  dim = c.dimensions
  if dim[0] == 30 and dim[1] == 10:
    whitespaceAgain(c, retry=True)
    print('!'*80)

print(f"{len(done)} done {len(todo)} remaining")
