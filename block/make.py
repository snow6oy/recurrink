import copy
import time
import pprint
from shapely.geometry import Polygon, LineString
from shapely import transform
from cell import Layer
from .meander import Meander
from .styles import Styles

class Make:

  VERBOSE = False
  BLOCKSZ = (3, 1)
  CLEN    = 9

  def __init__(self, clen=0): 
    self.cells  = dict()
    self.style  = Styles()
    self.guide  = dict()
    self.grid   = [{} for _ in range(3)] # unique style for each layer
    if clen: self.CLEN = clen


  def walk(self, positions, cells):
    ''' navigate the model and populate cells
    '''
    self.setBlocksize(positions)
    for pos in positions:
      label = positions[pos][0]  
      cell  = Layer(clen=self.CLEN, pos=pos)
      cell.background()

      # swap some colours
      if cells[label]['shape'] == 'sqring':
        cells[label]['bg']   = cells[label]['fill'] 
        cells[label]['fill'] = None 
        cell.direction[0]    = ('spiral', None)
      # TODO can Styles help make the hole invisible? alpha=0 fill_opacity
      self.style.add(pos, 
        fill=cells[label]['bg'], stroke=cells[label]['bg'],
        stroke_opacity=1, stroke_width=0.7
      )

      for label in positions[pos]:
        if not label: continue
        if bool(cells[label]['top']):
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, 
            fill=cells[label]['fill'],
            stroke=cells[label]['stroke'],
            stroke_dasharray=cells[label]['stroke_dasharray'],
            stroke_opacity=cells[label]['stroke_opacity'],
            stroke_width=cells[label]['stroke_width']
          )
        else:
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, 
            fill=cells[label]['fill'],
            stroke=cells[label]['stroke'],
            stroke_dasharray=cells[label]['stroke_dasharray'],
            stroke_opacity=cells[label]['stroke_opacity'],
            stroke_width=cells[label]['stroke_width']
          )
      self.cells[pos] = cell.polygon()
      self.guide[pos] = cell.direction

  def meanderSpiral(self, cell, pos):
    m = Meander(cell)
    linestr = LineString(m.spiral(self.CLEN, pos))
    return linestr

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
    ed        = ed if clockwise else list(reversed(ed))
    gnomon    = Meander(composite.geoms[0])
    if padding: gnomon.pad()
    g_guide   = gnomon.guidelines(gd)
    g_points  = gnomon.collectPoints(g_guide)

    edge      = Meander(composite.geoms[1])
    if padding: edge.pad()
    e_guide   = edge.guidelines(ed)
    e_points  = edge.collectPoints(e_guide)
    return edge.joinStripes(g_points, e_points)

  def meanderGuided(self, cell, guide, padding):
    ''' orchestrate the guided algorithm of meander
    '''
    m      = Meander(cell)
    padme  = m.pad() if padding else m.shape
    gline  = m.guidelines(guide, shape=padme)  # ('EB', 'ET'))
    points = m.collectPoints(gline, shape=padme)
    return LineString(m.makeStripes(points))

  def meander(self, padding=True):
    ''' transform polygons into lines
    '''
    for z in range(3): # bg 0 fg 1 top 2
      for pos in self.cells:
 
        polygn = self.polygon(pos, z)
        if polygn is None: continue

        algo, *guide  = self.guide[pos][z]
        #print(f'{z} {pos} {algo} {time.time()}')
        if algo == 'spiral':
          linestr = self.meanderSpiral(polygn, pos)
        elif algo == 'composite':
          linestr = self.meanderComposite(guide, pos, padding=padding)
        elif algo == 'guided':
          linestr = self.meanderGuided(polygn, guide, padding=padding)
        else:
          raise Warning(f"{pos} {z} {algo} not known to Meander")
        self.guide[pos][z] = linestr # replace guide with Shapely.LineString

  def setBlocksize(self, positions):
    ''' extract blocksize and set for downstream functions
    '''
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

  def polygon(self, pos, z): 
    ''' lookup cell in layer
    '''
    c = self.cells[pos]

    if z == 2 and len(c.geoms) > 2: polygn = c.geoms[2]
    elif z == 2: polygn = None
    elif z == 1 and len(c.geoms) > 1:
      polygn = c.geoms[1]
    elif z == 1 and len(c.geoms[0].interiors):
      polygn = Polygon(c.geoms[0].interiors[0])
    elif z == 0: polygn = c.geoms[z]     # bg
    return polygn

  def __hydrateGrid(self):
    ''' convert one block into a list of polygons
        each list has a unique style for each layer
        0 s1 [p1 p2], s2 [p1]
    '''
    for pos in self.cells:
      for z in range(len(self.cells[pos].geoms)):
        #print(z, pos)
        fill   = self.style.fill[pos][z]
        style  = f'fill:{fill};fill-opacity:0.5'
        polygn = self.polygon(pos, z)
        if style in self.grid[z]:
          self.grid[z][style].append(polygn)
        else:
          self.grid[z][style] = list()
          self.grid[z][style].append(polygn)
    #pprint.pprint(self.grid)
    return None
 
  def hydrateGrid(self, line=False):
    ''' convert one block into a list of polygons
        each list has a unique style for each layer
        0 s1 [p1 p2], s2 [p1]
    '''
    for z in range(3): 
      for pos in self.cells:
        print(z, pos)
        polygn = self.polygon(pos, z)
        if not polygn: continue
        if line:
          f = 'fill:none;'
          s = f'stroke:{self.style.stroke[pos][z]};'
          d = f'stroke-dasharray:{self.style.stroke_dasharray[pos][z]};'
          o = f'stroke-opacity:{self.style.stroke_opacity[pos][z]};'
          w = f'stroke-width:{self.style.stroke_width[pos][z]};'

          style  = f + s + d + o + w
          geom   = self.guide[pos][z]    # fetch linestring
        else:
          fill   = self.style.fill[pos][z]
          style  = f'fill:{fill};fill-opacity:0.5'
          geom   = polygn                # assign polygon
        if style in self.grid[z]:
          self.grid[z][style].append(geom)
        else:
          self.grid[z][style] = list()
          self.grid[z][style].append(geom)
    #pprint.pprint(self.grid)
    return None
 
'''
the
end
'''
