from shapely.geometry import Polygon

class Diamond():
  def __init__(self):
    self.name = 'diamond'

  def coords(self, points, geom):

    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    facing = geom['facing']
    rings  = {
        'all': (w, n, e, s), 'C': (w, n, e, s),
       'west': (w, n, s),    'W': (w, n, s),
       'east': (n, e, s),    'E': (n, e, s),
      'north': (w, n, e),    'N': (w, n, e),
      'south': (w, e, s),    'S': (w, e, s)
    }
    if facing in rings:
      return Polygon(rings[facing])
    else:
      raise IndexError(f"Cannot face diamond {facing}")

  def validate(self, geom):
    if geom['size'] in ['large', 'small']: 
      return 'wrong size'

  def guide(self, facing): return ('border', None)

'''
the
end
'''
