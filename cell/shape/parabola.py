import pprint
from shapely import line_merge
from shapely.geometry import Polygon, LineString, MultiLineString
from cell.meander import Line

class Parabola(Line):
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.name = 'parabola'
    super().__init__()

  def validate(self, geom): pass

  def coords(self, dim, geom):
    ''' define the input so Shapely Polygon can create a U shape
    '''
    X, Y, W, H, a, b, c, d, *A = dim

    facing    = geom['facing']
    direction = {
          'N': [(X,Y),(X,H),(W,H),(W,Y),(c,Y),(c,d),(a,d),(a,Y)],
          'S': [(X,Y),(X,H),(a,H),(a,b),(c,b),(c,H),(W,H),(W,Y)],
          'W': [(X,Y),(X,H),(W,H),(W,d),(a,d),(a,b),(W,b),(W,Y)],
          'E': [(X,Y),(X,b),(c,b),(c,d),(X,d),(X,H),(W,H),(W,Y)]
    }
    return Polygon(direction[facing])

  def draw(self, clen, dim, geom, padding=False):
    ''' orchestrate the composite algorithm of meander
    '''
    X, Y, W, H, a, b, c, d, *A = dim
    facing  = geom['facing']
    control = {
      'N': ['NE', 'W', X, Y, a, d],  # test g
      'S': ['SW', 'E', c, b, W, H],  # test h
      'E': ['SE', 'N', X, d, c, H],  # test i
      'W': ['NW', 'S', a, Y, W, b]   # test f
    }
    # facing for the composites
    if facing in control: gface, eface = control[facing][:2]
    else: raise KeyError(f'all at sea > {facing} < without control')
    if self.VERBOSE: print(f'{gface=} {eface=} {facing=}')

    bounds  = dim[:4]
    guideln = self.guidelines(gface, clen, bounds)
    points  = self.collectPoints(guideln)
    linstr  = self.makeStripes(points)
    sliced  = self.sliceByThird(gface, linstr.coords)
    gnomon  = LineString(sliced)

    bounds  = control[facing][2:]
    guideln = self.guidelines(eface, clen, bounds)
    points  = self.collectPoints(guideln)
    edge    = self.makeStripes(points)
    joined  = self.joinStrings(gnomon, edge)
    return joined

  def reString(self, linstr, point, reverse=False, append=False, case=0):
    ''' help simplify join strings
    '''
    coords = list(linstr.coords)
    if reverse: coords = list(reversed(coords))
    if append:
      coords.append(point)
    else:
      coords.insert(0, point)
    if case and self.VERBOSE: print(f'restrung case #{case}')
    return LineString(coords)

  def joinStrings(self, gnomon, edge):
    ''' join two line strs into a single line

    test with recurrink
    document and commit
    '''
    g1, g2 = list(gnomon.boundary.geoms)
    e1, e2 = list(edge.boundary.geoms)
    if g2.x == e1.x or g2.y == e1.y: 
      gnomon = self.reString(gnomon, e1, append=True, case=1)
    elif g1.x == e1.x or g1.y == e1.y: 
      gnomon = self.reString(gnomon, e1, reverse=True, append=True, case=2)
    elif g2.x == e2.x or g2.y == e2.y: 
      edge = self.reString(edge, g2, reverse=True, append=False, case=3)
    elif g1.x == e2.x or g1.y == e2.y: 
      gnomon = self.reString(gnomon, e2, reverse=True, append=True, case=3)
    elif self.VERBOSE: 
      print(f'''
failed to find a matching condition
{g1.x=} {g1.y=} {g2.x=} {g2.y=}
{e1.x=} {e1.y=} {e2.x=} {e2.y=}''')
      
    mls    = MultiLineString([gnomon, edge])
    ''' mls is ok to return for matplot but not model.linear
    return mls
    ''' 
    stripe = line_merge(mls)
    if stripe.geom_type != 'LineString':
      raise TypeError(f"""
line merge failed {stripe.geom_type} is wrong type. 
""")
    return stripe
'''
the
end
'''
