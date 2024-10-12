from shapely.geometry import box, LinearRing, Polygon
import matplotlib.pyplot as plt
''' test Shapely.within() works as expected
'''
def make_boxen(x, y, w, h):
  return box(x, y, w, h)

def make_lines(x, y, w, h):
  return LinearRing([(x, y), (x, y + h), (x + w, y + h), (x + w, y), (x, y)])

blue = make_boxen(2.0, 2.0, 3.0, 3.0)
b = make_lines(2.0, 2.0, 3.0, 3.0)
red = make_boxen(0.0, 3.0, 3.0, 1.0)
r = make_lines(0.0, 3.0, 3.0, 1.0)
t = 1

if t == 0:
  ''' send red blue to matplot
  '''
  print(f"red is within blue = {red.within(blue)}")  # should be False
  fig, ax = plt.subplots() 
  rx, ry = r.xy
  bx, by = b.xy
  plt.plot(rx, ry, 'r-', bx, by, 'b--')
  plt.show()
elif t == 1:
  ''' boxen
  '''
  print(blue.geom_type)
  print(list(blue.exterior.coords))
  print(list(blue.bounds))
  print(blue.area)
  # print(blue.xy) .xy is not an attribute of box
elif t == 2:
  ''' linear ring makes a gnomon
  '''
  r = LinearRing(
    [(1,1), (1,3), (3,3), (3,2), (2,2), (2,1), (1,1)]
  )
  print(r.geom_type)
  print("ring bounds")
  print(r.bounds)
  print("ring .xy")
  print(r.xy)  # only works on LinearRing, box and Polygon say not impl
  ''' polygon from ring
  '''
  print()
  p = Polygon(r)
  print(p.geom_type)
  print(p.is_valid)  # returns True 
  print(p.area)
  print(r.area) # lines contain empty space
  fig, ax = plt.subplots() 
  rx, ry = r.xy
  #px, py = p.xy
  plt.plot(rx, ry, 'r-') #, px, py, 'b--')
  plt.show()
  '''
  '''
elif t == 3:
  nw_se=LineString([(0, 1), (1, 0)])
  ne_sw=LineString([(1, 1), (0, 0)])
  print(type(nw_se))
  print(nw_se.crosses(ne_sw))
