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

  def joinStripes(self, p1, p2):
    ''' orchestrate make stripes calls and join two points
    '''
    s1       = self.makeStripes(p1)
    last_p1  = list(s1.coords)[-1] # sort the points before marking the last
    s2       = self.makeStripes(p2)
    s2       = list(s2.coords)      # extract list from LineString 
    s2       = list(reversed(s2))   # 
    first_p2 = s2[0]
    if self.VERBOSE: print(f'{last_p1=} {first_p2=}')
    s2.insert(0, last_p1)           # guess that last p1 matches first p2
    s2       = LineString(s2)
    mls      = MultiLineString([s1, s2])

    stripe  = line_merge(mls)
    if stripe.geom_type != 'LineString':
      raise TypeError(f"""
line merge failed {stripe.geom_type} is wrong type. Check {last_p1=} {first_p2=}
""")
    return stripe

  def draw(self, facing, clen, dim, padding=False):
    ''' orchestrate the composite algorithm of meander
    '''
    X, Y, W, H, a, b, c, d, *A = dim
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
    print(f'{bounds=}')
    guideln = self.guidelines(gface, clen, bounds)
    points  = self.collectPoints(guideln)
    linstr  = self.makeStripes(points)
    gnomon  = self.sliceByThird(gface, linstr.coords)
    '''
    self.pp.pprint(gnomon)
    '''

    bounds  = control[facing][2:]
    guideln = self.guidelines(eface, clen, bounds)
    points  = self.collectPoints(guideln)
    edge    = self.makeStripes(eface, points)
    linestr = self.joinStripes(gnomon, edge)
    return linstr

  def _draw(self, facing, clen, dim, padding=False):
    ''' cannot pass MLS to model/linear
    '''
    X, Y, W, H, a, b, c, d, *A = dim
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
    gnomon  = self.sliceByThird(gface, linstr.coords)

    bounds  = control[facing][2:]
    guideln = self.guidelines(eface, clen, bounds)
    points  = self.collectPoints(guideln)
    edge    = self.makeStripes(points)
    return LineString(gnomon)
    '''
    mls     = MultiLineString([gnomon, edge])
    return line_merge(mls)
    '''

'''
the
end
'''
