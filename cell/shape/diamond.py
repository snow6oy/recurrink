from shapely.geometry import Polygon

class Diamond:
  def __init__(self):
    self.name = 'diamond'

  def coords(self, points, geom):

    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    facing = geom['facing']
    rings  = {
          'C': (w, n, e, s),
          'W': (w, n, s),
          'E': (n, e, s),
          'N': (w, n, e),
          'S': (w, e, s)
    }
    """
        'all': (w, n, e, s), 
       'west': (w, n, s),
       'east': (n, e, s),
      'north': (w, n, e),
      'south': (w, e, s),
    """
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
