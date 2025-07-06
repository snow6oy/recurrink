from shapely.geometry import Polygon, LineString
from cell import Layer
from .meander import Meander
from .styles import Styles

class Make:

  VERBOSE = True
  BLOCKSZ = (3, 1)
  CLEN    = 6

  def __init__(self, clen=0): 
    self.cells  = dict()
    self.style  = Styles()
    self.guide  = dict()
    if clen: self.CLEN = clen

  def walk(self, positions, cells):
    ''' navigate the model and populate cells
    '''
    self.setBlocksize(positions)
    for pos in positions:
      cell = Layer(clen=self.CLEN, pos=pos)
      cell.background()
      label = positions[pos][0]
      self.style.add(pos, fill=cells[label]['bg'])

      for label in positions[pos]:
        if not label: continue
        if bool(cells[label]['top']):
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, fill=cells[label]['fill'])
        else:
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, fill=cells[label]['fill'])
      self.cells[pos] = cell.polygon()
      self.guide[pos] = cell.direction

  def meander(self, padding=True):
    # can use style as a skeleton to access lring ?
    ''' transform polygons into lines
    '''
    for z in range(3): # bg 0 fg 1 top 2
      for pos, c in self.cells.items():

        if z == 2 and len(c.interiors) > 1: 
          lring = c.interiors[1]                   # top
        elif z == 2: continue 
        elif z == 1: lring = c.interiors[0]        # fg
        elif z == 0: lring = c.exterior            # bg

        if self.VERBOSE: 
          print(f"{z=} {pos=} {len(c.interiors)} {self.guide[pos][z]}")

        algo, *guide  = self.guide[pos][z]
        if algo == 'spiral':
          m       = Meander(Polygon(lring))
          linestr = LineString(m.spiral(self.CLEN, pos))
        elif algo == 'composite':
          linestr = self.meanderComposite(guide, pos, padding=padding)
        elif algo == 'guided':
          linestr = self.meanderGuided(guide, lring, padding=padding)
        else:
          raise Warning(f"{pos} {z} {algo} not known to Meander")
        self.guide[pos][z] = linestr # replace guide with Shapely.LineString

  # TODO padding
  def meanderComposite(self, meta, pos, padding):
    ''' orchestrate the composite algorithm of meander
    '''
    f1, f2 = meta # facing for the composites
    cell   = Layer(clen=self.CLEN, pos=pos)
    cell.foreground(shape='gnomon', facing=f1, size='medium')
    cell.foreground(shape='edge',   facing=f2, size='small')

    clockwise = cell.setClock(padding=padding)
    composite = cell.polygon()
    gd        = cell.direction[0][1:]  # ignore algo
    gd        = gd if clockwise else list(reversed(gd))
    ed        = cell.direction[1][1:]
    #ed        = list(reversed(ed)) if clockwise else ed
    ed        = ed if clockwise else list(reversed(ed))
    gnomon    = Meander(Polygon(composite.exterior))
    if padding: gnomon.pad()
    g_guide   = gnomon.guidelines(gd)
    g_points  = gnomon.collectPoints(g_guide)

    edge      = Meander(Polygon(composite.interiors[0]))
    if padding: edge.pad()
    e_guide   = edge.guidelines(ed)
    e_points  = edge.collectPoints(e_guide)
    return edge.joinStripes(g_points, e_points)

  def meanderGuided(self, guide, lring, padding):
    ''' orchestrate the guided algorithm of meander
    '''
    m      = Meander(Polygon(lring))
    padme  = m.pad() if padding else m.shape
    gline  = m.guidelines(guide, shape=padme)  # ('EB', 'ET'))
    points = m.collectPoints(gline, shape=padme)
    return LineString(m.makeStripes(points))

  def setBlocksize(self, positions):
    ''' extract blocksize and set for downstream functions
    '''
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

'''
the
end
'''
