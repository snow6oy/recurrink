import pprint
import xml.etree.ElementTree as ET
from shapely import transform
from shapely.geometry import Polygon

class SvgModel:
 
  ''' A3 297 x 420
      A2 420 x 594
      reduced by 40mm for border when CLEN = 20 and scale 1
  '''
  PAPERSIZE = {
    'A3P': (297, 420),
    'A3L': (420, 297),
    'A3S': (297, 297),
    'A2P': (420, 594),
    'A2L': (594, 420),
    'A2S': (420, 420),
  }
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent = 2)

  def __init__(self, clen, scale=1.0, ps=None):
    if not ps: ps = 'A3L'
    print(f'{clen=} {scale=} {ps=}')
    scaled      = clen * scale
    margin      = scaled * 2  # margin = length of one cell after scaling
    max_len     = (
      self.PAPERSIZE[ps][0] - margin, self.PAPERSIZE[ps][1] - margin
    )
    print(f'{clen=} {scaled=} {max_len=}')
    if scaled % 2:
      print(f'WARNING {clen} not divisible by 2: may not pass meander')
    elif scaled < 3 or scaled > 90:
      raise ValueError(f'{clen=} * {scale=} exceeded safe limit')
    self.border = 0
    self.grid   = list()
    self.unit   = 'mm'
    self.scaled = scaled
    self.clen   = clen

    cellnum     = (round(max_len[0] / scaled), round(max_len[1] / scaled))
    gridsz      = (int(cellnum[0] * scaled), int(cellnum[1] * scaled))
    viewbx      = (int(cellnum[0] * clen), int(cellnum[1] * clen))

    self.gridsz = (gridsz[0], gridsz[1])
    self.viewbx = (viewbx[0], viewbx[1])

  def explode(self, block):
    ''' prepare model by copying block.grid to exploded self
    '''
    b0, b1  = block.BLOCKSZ
    edge    = (self.viewbx[0], self.viewbx[1])
    cellnum = (int(edge[0] / self.clen), int(edge[1] / self.clen))

    for z, layer in enumerate(block.grid):
      self.grid.append({})
      for style in layer:
        self.grid[z][style] = {'geom':list(), 'penam':str()}
        exploded = self.walk(
          layer[style]['geom'], cellnum, b0, b1, self.clen, edge
        )
        self.grid[z][style]['geom']  = exploded
        self.grid[z][style]['penam'] = layer[style]['penam']

  def walk(self, block, cellnum, b0, b1, CLEN, edge):
    cells = list()
    for y in range(0, cellnum[1], b1):
      for x in range(0, cellnum[0], b0):
        for p in block:  # loop the polygons
          ''' all cells in block use same x,y coord for transform
          '''
          clone    = transform(p, lambda xy: xy + [x * CLEN, y * CLEN])
          X, Y, *Z = clone.bounds     # check if we went over the edge
          if X >= CLEN and X <= edge[0] and Y >= CLEN and Y <= edge[1]:
            cells.append(clone)
            if self.VERBOSE: print(f"{X:2.0f} {Y:2.0f}, ", end='', flush=True)
      if self.VERBOSE: print()
    return cells

  def build(self, block):
    ''' like explode but just one block, more like a pop
    '''
    b0, b1      = block.BLOCKSZ
    self.grid   = block.grid
    self.border = 2
    self.gridsz = (b0 * self.scaled, b1 * self.scaled)
    self.viewbx = (b0 * self.clen,   b1 * self.clen)

  def setSvgHeader(self):
    ''' start the markup
    '''
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    w, h = self.gridsz
    W, H = self.viewbx
    unit = self.unit
    b    = self.border
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 {W} {H}" 
      width="{w}{unit}" height="{h}{unit}"
      style="border: {b}{unit} solid #000000;"></svg>
    ''')
    # transform="scale(1)" has not effect ?
    comment = ET.Comment(f' cell length: {self.clen}')
    root.insert(0, comment)  # 0 is the index where comment is inserted
    #ET.dump(root)
    self.ns = '{http://www.w3.org/2000/svg}'
    self.root = root

  def render(self, model, line=False):
    ''' render SVG grouped by colour for pen plotting
    pp.pprint(self.grid[0].keys())
    '''
    self.setSvgHeader()
    inner_p = list()
    elem    = 'polyline' if line else 'polygon'
    uniqid  = 1 # xml elements must have unique IDs

    for layer in self.grid:
      for style in layer:
        # TODO
        ''' group ID should be the name of the pen e.g. S68-034
            to show 1mm stripes in gthumb set stroke-width:0.5 ??
        '''
        g = ET.SubElement(self.root, f"{self.ns}g", id=layer[style]['penam'])
        g.set('style', style)  # 'fill:#FFF;stroke:#000;stroke-width:1'
        for shape in layer[style]['geom']:
          ''' SVG polygon
          print(shape.geom_type)
          '''
          uniqid += 1
          p  = ET.SubElement(g, f"{self.ns}{elem}", id=str(uniqid))
          points = str()
          #if not line and len(shape.interiors): # Square Ring has a hole
          # Square Ring has a hole
          if shape.geom_type == 'Polygon' and len(shape.interiors): 
            outer  = list(shape.exterior.coords)
            inner  = list(shape.interiors)
            coords = outer 
            [inner_p.append(list(lring.coords)) for lring in inner]
          elif shape.geom_type == 'Polygon':
            coords = list(shape.boundary.coords)
          else: # should be LineString
            coords = list(shape.coords)
          #if uniqid == 52: print(style) # t.block_build.Test.bb_test_e
          for c in coords:
            coord = ','.join(map(str, c))
            points += f"{coord} "
          p.set("points", points.strip())
        uniqid += 1
        ''' fill in the holes
        '''
        if len(inner_p) > 0:
          g = ET.SubElement(self.root, f"{self.ns}g", id=layer[style]['penam'])
          # 'fill:#FFF;stroke:#000;stroke-width:1;stroke-dasharray:0.5')
          g.set('style', style)
        for coords in inner_p:  
          uniqid += 1
          # Add any points from inner ring
          p      = ET.SubElement(g, f"{self.ns}{elem}", id=str(uniqid))
          points = str()
          for c in coords:
            coord = ','.join(map(str, c))
            points += f"{coord} "
            p.set("points", points.strip())
    self.write(f'tmp/{model}.svg')

  def write(self, svgfile):
    tree = ET.ElementTree(self.root)
    ET.indent(tree, level=0)
    tree.write(svgfile)

'''
the
end
'''
