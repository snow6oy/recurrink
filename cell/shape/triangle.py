from shapely.geometry import Polygon

class Triangle():
  ''' a linear ring wrapped in a Polygon 
      the wrapper is needed by transform
  '''
  def __init__(self):
    self.name = 'triangl' # misspelt due to 7char limit when CSV

  def coords(self, points, geom):

    swidth, clen, n, e, s, w, ne, se, nw, sw, mid = points
    facing = geom['facing']
    rings = {
      'N': (nw, ne, s),
      'S': (sw, n, se),
      'E': (nw, e, sw),
      'W': (w, ne, se)
    }
    """
      'north': (nw, ne, s),
      'south': (sw, n, se),
      'east': (nw, e, sw),
      'west': (w, ne, se),
    """
    if facing in rings:
      return Polygon(rings[facing])
    else: raise IndexError(f"Cannot face triangle {facing}")

  def validate(self, geom):
    if geom['facing'] == 'C':
      return 'cannot face Centre'
    if geom['size'] in ['small', 'large']:
      return 'wrong size'

  def guide(self, facing): return ('border', None)

'''
the
end
'''
