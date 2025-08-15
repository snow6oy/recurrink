import math
from shapely.geometry import Point

class Circle():
  ''' circle plots badly (square wheels!) as Shape.draw()
      sets precision to whole number
      but aside from testing, it matters not as 
      the SVG output is smooth
  '''
  def __init__(self):
    self.name = 'circle'

  def coords(self, points, geom):
    swidth, clen, n, e, s, w, ne, se, nw, nw, mid = points
    size  = geom['size']
    large = clen / 2
    ''' pythagoras was a pythonista :)
    '''
    sum_two_sides = (large**2 + large**2)
    sizes = {
       'large': (math.sqrt(sum_two_sides) - swidth),
      'medium': (clen / 2 - swidth),
       'small': (clen / 3 - swidth)
    }
    if size in sizes:
      radius = sizes[size]
      x, y   = mid
      return Point(x, y).buffer(radius)
    else:
      raise IndexError(f"Cannot set circle to {size} size")

  def validate(self, geom):
    if geom['facing'] != 'C': return 'must face all'

  def guide(self, facing): return ('border', None)

'''
the
end
'''
