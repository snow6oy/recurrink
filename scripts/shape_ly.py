from shapely import box, LinearRing, LineString, MultiLineString, Polygon, Point, set_precision, transform
import matplotlib.pyplot as plt

def make_boxen(x, y, w, h):
  return box(x, y, w, h)

def make_lines(x, y, w, h):
  return LinearRing([(x, y), (x, y + h), (x + w, y + h), (x + w, y), (x, y)])

def t(blue, red):
  print(f"{blue.overlaps(red)=}")
  print(f"{blue.intersects(red)=}")
  print(f"{blue.crosses(red)=}")
  print(f"{blue.contains(red)=}")
  print(f"{blue.touches(red)=}")
  print(f"{blue.within(red)=}")

blue = make_boxen(2.0, 2.0, 3.0, 3.0)
b = make_lines(2.0, 2.0, 3.0, 3.0)
red = make_boxen(0.0, 3.0, 3.0, 1.0)
r = make_lines(0.0, 3.0, 3.0, 1.0)

# first use-case
blue_sq = LinearRing([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
red_one = LinearRing([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0), (0, 0)])
# first use-case as polygons
blue_sq_p = Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
red_one_p = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0), (0, 0)])
# second use-case
blue_ln = LinearRing([(2, 1), (2, 2), (7, 2), (7, 1), (2, 1)])
red_two = LinearRing([(1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 0), (1, 0)])
# second use-case as polygons
#blue_ln_p = Polygon([(2, 1), (2, 2), (7, 2), (7, 1), (2, 1)])
blue_ln_p = Polygon(blue_ln)
red_two_p = Polygon([(1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 0), (1, 0)])

a1 = LineString([(3, 0), (3, 2)])
b1 = LineString([(2, 1), (7, 1)])
a2 = LineString([(3, 0), (3, 2)])
b2 = LineString([(2, 2), (7, 2)])

p1 = Polygon([(8.0, 2.0), (8.0, 1.0), (7.0, 1.0), (2.0, 1.0), (2.0, 2.0), (7.0, 2.0), (8.0, 2.0)])
p2 = Polygon([(1.0, 1.0), (1.0, 2.0), (2.0, 2.0), (7.0, 2.0), (7.0, 1.0), (2.0, 1.0), (1.0, 1.0)])

case = 12

if case == 1:
  ''' using overlap predicate with Polygons can detect difference 
  '''
  print('Lines')
  t(blue_sq, red_one)
  print('-'*80)
  t(blue_ln, red_two)
  print('Polygons')
  t(blue_sq_p, red_one_p)
  print('-'*80)
  t(blue_ln_p, red_two_p)
elif case == 2:
  # crossing Line Strings works
  print(f"{a1.crosses(b1)=}")
  print(f"{a2.crosses(b2)=}")
  print(list(a1.coords))
elif case == 3:
  ''' make the blue square from four sides
  '''
  blue_sq_mls = MultiLineString([
    LineString([(1.0, 1.0), (1.0, 2.0)]),
    LineString([(1.0, 2.0), (2.0, 2.0)]),
    LineString([(2.0, 2.0), (2.0, 1.0)]),
    LineString([(2.0, 1.0), (1.0, 1.0)])
  ])
  print(blue_sq_mls)
elif case == 4:
  ''' intersection is like Flatten().split ? 
  '''
  print(blue_sq.boundary)
  print(blue_sq.intersection(red_one))
  print(blue_ln.intersection(red_two))
elif case == 5:
  ''' merging Polygons is best
  '''
  print('Lines')
  t(blue_sq, blue_ln)
  merge_d = blue_sq.union(blue_ln)
  print(list(merge_d.geoms)) # lines in and lines out
  print('-'*80)
  print('Polygons')
  t(blue_sq_p, blue_ln_p)
  p = blue_sq_p.union(blue_ln_p)
  print(p.boundary)
  print(f"{p.geom_type=}") # Polygon has more predicates
  print(p)
elif case == 6:
  ''' test Shapely.within() works as expected
      send red blue to matplot
  '''
  print(f"red is within blue = {red.within(blue)}")  # should be False
  fig, ax = plt.subplots() 
  rx, ry = r.xy
  bx, by = b.xy
  plt.plot(rx, ry, 'r-', bx, by, 'b--')
  plt.show()
elif case == 7:
  ''' boxen
  '''
  print(blue.geom_type)
  print(list(blue.exterior.coords))
  print(list(blue.bounds))
  print(blue.area)
  # print(blue.xy) .xy is not an attribute of box
elif case == 8:
  ''' linear ring makes a gnomon
  '''
  r = LinearRing(
    [(1,1), (1,3), (3,3), (3,2), (2,2), (2,1), (1,1)]
  )
  print(r.geom_type)
  print("ring bounds")
  print(r.bounds)
  print("ring .xy")
  print(r.xy)  # only works on LinearRing, use .boundary for box and Polygon
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
elif case == 9:
  nw_se=LineString([(0, 1), (1, 0)])
  ne_sw=LineString([(1, 1), (0, 0)])
  print(type(nw_se))
  print(nw_se.crosses(ne_sw))
elif case == 10:
  t(p1, p2)
elif case == 11:
  ''' buffer can make padding
  '''
  # p = Polygon([(1, 1), (1, 20), (20, 20), (20, 1)]) 
  p = Polygon([(1,1), (1,30), (30,30), (30,20), (20,20), (20,1)])
  print(p.boundary)
  px, py = p.boundary.xy
  p1 = p.buffer(-1, single_sided=True)
  b = set_precision(p1, 2.0)
  print(b.boundary)
  fig, ax = plt.subplots() 
  bx, by = b.boundary.xy
  plt.plot(px, py, 'blue', bx, by, 'r--')
  plt.show()
elif case == 12:
  '''
  tx = transform(Point(0, 0), lambda x: x + 1)
  tx = sq.boundary.transform(lambda x: x + 1)
  print(tx)
  '''
  sq = Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
  print(sq.boundary)
  ls = LineString([(2, 2), (4, 4)])
  l2 = transform(ls, lambda x: x * [2, 3])
  print(ls, l2)
elif case == 13:
  ''' svg
  '''
  print(blue.geom_type)
  print(blue.svg())
  blue.svg(scale_factor=2.0, fill_color='#FF0', opacity=0.5)
  print(blue.svg())





