import pprint
from shapely.geometry import Polygon, LineString, MultiPolygon
from cell import Layer
from .styles import Styles

class Make:

  VERBOSE = False
  BLOCKSZ = (3, 1)
  CLEN    = 9
  pp      = pprint.PrettyPrinter(indent=2)

  def __init__(self, clen=9, linear=False, pen_names=dict()): 
    self.cells  = dict()
    self.style  = Styles(pen_names)
    self.linear = linear
    #self.guide  = dict()
    self.grid   = [{} for _ in range(3)] # unique style for each layer
    if clen: self.CLEN = clen

  def walk(self, positions, cells):
    ''' navigate the model and populate cells
    '''
    self.setBlocksize(positions)
    for pos in positions:
      label   = positions[pos][0]  
      cell    = Layer(clen=self.CLEN, pos=pos, linear=self.linear)
      cell.background(cells[label])
      ''' ['geom']) if cells[label]['color']['background']: 
      print(f"{label} {cells[label]['color']['background']}")
      '''
      self.style.addBackground(pos, color=cells[label]['color'])
      for label in positions[pos]:
        if not label: continue
        if 'stroke' in cells[label]: strokedata = cells[label]['stroke']
        else: strokedata = None
        if bool(cells[label]['geom']['top']):
          cell.foreground(cells[label]['geom'])
          self.style.add(pos, color=cells[label]['color'], stroke=strokedata)
        else:
          cell.foreground(cells[label]['geom'])
          self.style.add(pos, color=cells[label]['color'], stroke=strokedata)
      self.cells[pos] = cell.bft

  def setBlocksize(self, positions):
    ''' extract blocksize and set for downstream functions
    '''
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

  def polygon(self, c, pos, z): 
    ''' lookup cell in layer
    '''
    if z == 2 and len(c.geoms) > 2: polygn = c.geoms[2]
    elif z == 2: polygn = None
    elif z == 1 and len(c.geoms) > 1:
      polygn = c.geoms[1]
    elif z == 1 and len(c.geoms[0].interiors):
      polygn = Polygon(c.geoms[0].interiors[0])
    elif z ==1:
      polygn = Polygon(c.geoms[0])
      # for g in c.geoms: print(f'{pos=} {z=} {g.geom_type}')
    elif z == 0: polygn = c.geoms[z]     # bg
    return polygn

  def hydrateGrid(self):
    ''' convert one block into a list of polygons
        each list has a unique style for each layer
        0 s1 [p1 p2], s2 [p1]
    '''
    for z in range(3): 
      for pos in self.cells:
        if z == len(self.cells[pos]): continue

        fill = self.style.fill[pos][z]
        if self.linear:
          f = 'fill:none;'
            # TODO what if there is a stroke ?
          s = f'stroke:{fill};'    
          d = f'stroke-dasharray:{self.style.stroke_dasharray[pos][z]};'
          o = f'stroke-opacity:{self.style.stroke_opacity[pos][z]};'
            # TODO fix tmpfile to support <1 self.style.stroke_width[pos][z]
            # w = f'stroke-width:{self.style.stroke_width[pos][z]};'
          w = f'stroke-width:0.7;' 

          style  = f + s + d + o + w
          geom   = self.cells[pos][z] # LineString

        else:
          style  = f'fill:{fill};fill-opacity:0.5'
          multip = MultiPolygon(self.cells[pos])
          geom   = self.polygon(multip, pos, z) # assign MultiPolygon

        if self.linear and geom.geom_type != 'LineString':
          raise TypeError(f'{geom.geom_type} not expected')

        if style in self.grid[z]:
          self.grid[z][style]['geom'].append(geom)
        elif self.style.fill[pos][z]:
          self.grid[z][style] = {
             'geom': list(), 
            'penam': self.style.fill_penam[pos][z] + f'_{z}'
          }
          self.grid[z][style]['geom'].append(geom)
        
    #self.pp.pprint(self.grid)
    return None
'''
the
end
'''
