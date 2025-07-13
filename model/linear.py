import copy
import pprint
import xml.etree.ElementTree as ET
pp = pprint.PrettyPrinter(indent = 2)
from shapely import transform
from shapely.geometry import Polygon

class SvgLinear:
  def __init__(self, clen):
    if clen % 9: raise ValueError(f'{clen} must divide by nine')
    self.clen        = clen
    self.grid        = [{} for _ in range(3)] # unique style for each layer
    self.gridsize_mm = 270

  def gridWalk(self, b1):
    ''' walk the grid, one block at a time
    '''
    cellnum     = int(self.gridsize_mm / self.clen)
    blocknum_x  = int(b1.BLOCKSZ[0] * clen) # blocksize in mm
    blocknum_y  = int(b1.BLOCKSZ[1] * clen)
    X = Y       = 0                         # lookup cell by block pos(X, Y)

    for y in range(0, self.gridsize_mm, self.clen):
      if y % blocknum_y: Y += 1 
      else: Y = 0 
      for x in range(0, self.gridsize_mm, self.clen):
        if x % blocknum_x: X += 1 
        else: X = 0 
        #print(f'{X:2d} {Y:2d}, ', end='', flush=True)
        pos = tuple([X, Y])
        if pos in b1.cells: self.stamp(x, y, b1.cells[pos])
        else: raise IndexError(f'{pos} not found')
      #print()

  def setSvgHeader(self):
    ''' start the markup
    '''
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    unit  = 'mm'
    w = h = self.gridsize_mm
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 {w} {h}" 
      width="{w}{unit}" height="{h}{unit}"
      transform="scale(1)"></svg>
    ''')
    comment = ET.Comment(f' cell length: {self.clen}')
    root.insert(0, comment)  # 0 is the index where comment is inserted
    #ET.dump(root)
    self.ns = '{http://www.w3.org/2000/svg}'
    self.root = root

  def render(self):
    ''' render SVG grouped by colour for pen plotting
    '''
    pp.pprint(self.grid[0].keys())
    self.setSvgHeader()
    inner_p = list()
    uniqid = 1 # xml elements must have unique IDs
    g      = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g.set('style', 'fill:#FFF;stroke:#000;stroke-width:1')
    for z in self.grid:
      gmk = done[i]
      uniqid += 1
      ''' SVG polygon
      '''
      p      = ET.SubElement(g, f"{self.ns}polygon", id=str(uniqid))
      points = str()
      # print(f"{shape_name=}")
      if gmk.label[0] == 'S':  # Square Ring is a multi part geometry
        outer  = list(gmk.shape.exterior.coords)
        inner  = list(gmk.shape.interiors)
        coords = outer 
        [inner_p.append(list(lring.coords)) for lring in inner]
      else:
        coords = list(gmk.shape.boundary.coords)
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
      p.set("points", points.strip())

    uniqid += 1
    g2 = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g2.set('style', 'fill:#FFF;stroke:#000;stroke-width:1;stroke-dasharray:0.5')
    for coords in inner_p:  
      uniqid += 1
      ''' Add any points from inner ring
      '''
      p      = ET.SubElement(g2, f"{self.ns}polygon", id=str(uniqid))
      points = str()
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
      p.set("points", points.strip())

  def stamp(self, x, y, cell):
    ''' replace relative positions with absolute and prepare shapes for SVG
        pos.z.shape > z.style.shape
    '''
    style = 'fill:#cccc33;fill-opacity:0.5'
    for z in range(len(cell.geoms)):
      #print(x, y, z)
      if cell.geoms[z].geom_type == 'Polygon':
        if len(cell.geoms[z].interiors) == 0:
          boundary = cell.geoms[z].boundary 
          lstring  = transform(boundary, lambda a: a + [x, y])
          polygn   = Polygon(lstring)
          #print(f"{x} {y}")
        elif len(cell.geoms[z].interiors) == 1: # deal with sqring
          lse = transform(cell.geoms[z].exterior, lambda a: a + [x, y])
          lsi = transform(cell.geoms[z].interiors[0], lambda a: a + [x, y])
          #print(f"{x} {y} {list(lsi.coords)}")
          polygn = Polygon(lse, holes=[list(lsi.coords)])
        else:
          raise NotImplementedError('too many holes in Polygon')

        if style in self.grid[z]:
          self.grid[z][style].append(polygn)
        else: 
          self.grid[z][style] = list()
          self.grid[z][style].append(polygn)
      else: raise TypeError(f"""{cell.geoms[z].geom_type} unexpected""")

class Layout:

  VERBOSE = False
  ''' the below cell sizes were calculated as
      gridsize / scale / cellnum
      18 was chosen as the preferred number of cells
      for both column and row with scale 1
      the num of cells is gridsize / cellsize

        PIXELS

        num of  cell           grid
         cells  size   scale   size
        ---------------------------------
             9 *  120    * 2.0 = 1080
            12 *   90    * 1.5 = 1080
            18 *   60    * 1.0 = 1080
            24 *   45    * .75 = 1080
            36 *   30    * 0.5 = 1080

        MILLIMETERS

             9 *   30    * 2.0 =  270
            18 *   15    * 1.0 =  270 
            36 *    9    * 0.6 =  270
  '''
  def __init__(self, unit='px', scale=1.0, gridsize=None, cellsize=None):

    self.governance = {
      'mm': { 'gridsize':270,  'cellsize':15, 'scale': [0.6, 1.0, 2.0] },
      'px': { 'gridsize':1080, 'cellsize':60, 
              'scale': [0.5, 0.75, 1.0, 1.5, 2.0] 
            }
    }
    msg = self.checksum(unit, scale, cellsize)
    if msg: raise ValueError(msg)
    gridsize      = gridsize if gridsize else self.governance[unit]['gridsize'] 
    cellsize      = cellsize if cellsize else self.governance[unit]['cellsize']
    self.unit     = unit
    self.scale    = float(scale)
    self.cellnum  = round(gridsize / (cellsize * scale))
    #print(f"{self.cellnum=} {gridsize=} {cellsize=} {scale=}")
    self.cellsize = round(cellsize * scale)
    self.gridsize = gridsize
    '''
    cell.bft[0] # background
    cell.bft[1] # foreground  USER GENERATED
    cell.bft[2] # or topless (.)(.) 
    cell.bft[n] #             MACHINE GENERATED 

    User-generated are layered (z axis) and constrained to MAX 3
    Machine-generated are 2D and constrained only by cellsize
    '''
    self.lstyles  = [{} for _ in range(3)] # unique style for each layer
    self.lgmk     = [{} for _ in range(3)] # unique gmk   for each layer
    self.seen     = str()    # have we seen this style before
    self.doc      = list()
    if False:           # run with gridsize=60 cellsize=6 to get a demo
      for col in range(self.cellnum):
        for row in range(self.cellnum):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()

  def checksum(self, unit, scale, cellsize):
    ''' sanity check the inputs
    '''
    if unit not in list(self.governance.keys()):
      return f'checksum failed: unknown unit {unit}'
    elif scale not in self.governance[unit]['scale']: # scale must in range
      return f'checksum failed scale {scale}'
    elif cellsize and (cellsize % 3): # cellsize / 3 must be a whole number
      return f'checksum failed cell size div by three {cellsize}'
    else:
      return None

  def trimStyle(self, style):
    start = style.index('#') + 1
    end = style.index(';')
    return style[start:end]

  ''' new gridWalk() 
  1. styleGuide to hydrate layer:cell:style
  2. stampBlocks to hydrate layer:cell:[gmk] each gmk has pos in grid
  3. compileDoc to combine style and [gmk] ordered by layer
  '''
  def styleGuide(self, block1, linear=False):
    ''' create a dict of styles:[cellnames]
        that are unique within each layer
        l0: a:s1 b: s2
        l1: a:s1 c: s3
    '''
    for pos in block1:
      cell = block1[pos]
      # print(f"{pos} {cell.x}")
      for li in range(len(cell.bft)): # li layer index
        style = cell.getStyle(li, linear)
        # print(f"  {li=} {style} {cell.bft[li].label}")
        self.addStyle(style, cell.bft[li].label, li)

  def addStyle(self, style, name, layer):
    ''' group geometries in SVG
        styles are unique for each layer 
    '''
    if layer >= len(self.lstyles):
      self.lstyles.append(dict()) # magically grow to accomodate computed shapes
    self.lstyles[layer][name] = style

  def _gridWalk(self, blocksize, block1):
    ''' walk the grid, one block at a time
    '''
    for y in range(0, self.cellnum, blocksize[1]):
      for x in range(0, self.cellnum, blocksize[0]):
        self.stampBlocks(blocksize, block1, tuple([x, y]))


  def stampBlocks(self, blocksize, block1, grid_xy):
    ''' position block in grid
    '''
    XY = tuple([(grid_xy[0] * self.cellsize), (grid_xy[1] * self.cellsize)])
    for col in range(blocksize[1]):
      for row in range(blocksize[0]):
        xy    = tuple([row, col])
        clone = copy.deepcopy(block1)  # copy whole block with nested objects
        cell  = clone[xy]
        [self.addGeomink(li, XY, layer) for li, layer in enumerate(cell.bft)]

  def addGeomink(self, li, pos, shape):
    ''' clone geominks then stash by layer and name
      print(f"{len(self.lgmk)=}")
    '''
    cn = shape.label
    if li >= len(self.lgmk): self.lgmk.append(dict())

    if shape.this.data is None: # avoid the void
      #print(f"avoiding {cn=} {pos=} {li=} ")
      self.lgmk[li][cn] = list()
      return
    if shape.this.data.geom_type == 'MultiPolygon': 
      print(f"ignoring multipolygon {cn} {len(shape.this.data.geoms)}")
      return
    shape.tx(pos[0], pos[1])

    if cn in self.lgmk[li]:
      self.lgmk[li][cn].append(shape)
    else:
      self.lgmk[li][cn] = list()
      self.lgmk[li][cn].append(shape)

  def svgDoc(self, meander=False):
    ''' pull objects from self and construct inputs to Svg()
        [ { shapes: [ {} {} ], style: fill:#00F } ]
    '''
    keys     = ['width', 'height', 'x', 'y', 'name']
    self.doc = list()
    di       = 0      # doc index
    for li, layer in enumerate(self.lgmk): # layer index
      seen = dict()                        # uniq style
      for cn in layer:                     # cell names in layer
        style = self.lstyles[li][cn]
        if style not in seen:
          seen[style] = di
          self.doc.append(dict())
          self.doc[di]['shapes'] = list()
          self.doc[di]['style']  = style
          di += 1
        dj = seen[style]
        for gmk in self.lgmk[li][cn]:
          name   = gmk.this.name
          if self.VERBOSE: print(f"{cn} {li} {name} {gmk.facing=}")
          shape  = gmk.svg(meander) 
          self.doc[dj]['shapes'].append(shape)

# TODO update Flatten to source block1 from Geomaker instead of here
class Grid(Layout):
  ''' inherit from Layout for governance of inputs
      same inputs must be shared with LinearSvg() see t.lineartest.Test.test_1 
  '''
  scale    = 1.0
  gridsize = 270
  cellsize = 15

  def __init__(self, unit='px', scale=1.0, gridsize=None, cellsize=None):
    super().__init__(
      unit='mm', scale=scale, gridsize=gridsize, cellsize=cellsize
    )

  def walk(self, blocksize, block1):
    ''' traverse the grid and use Shapely transform function 
        to stamp block1 into position
    '''
    blocks  = []
    b0, b1  = blocksize
    cellnum = round(self.gridsize / (self.cellsize * self.scale))
    grid_mm = int(cellnum * self.cellsize)
    x_block = int(b0 * self.cellsize)
    y_block = int(b1 * self.cellsize)
    print(f"{len(block1)=}")
    print(f"""
{blocksize=} {cellnum=} {grid_mm=} {self.cellsize=} {x_block=} {y_block=}""")
    for y in range(0, grid_mm, y_block):
      for x in range(0, grid_mm, x_block):
        block = list()
        for cell in block1:
          clone  = copy.copy(cell)
          clone.tx(x, y)
          block.append(clone)
          cb     = clone.shape.bounds
        blocks.append(block)
    return blocks

class Svg(Layout):
  def __init__(
    self, scale=1, unit='px', gridsize=0, cellsize=0, inkscape=False
  ):
    ''' svg:transform(scale) is better than homemade scaling
        but is lost when converting to raster. Instagram !!!
    '''
    square = True
    if type(gridsize) is tuple: # quick hak to make nicer wireframes
      w, h      = gridsize
      gridsize  = None
      square    = False # custom width and height 
      
    super().__init__(unit, scale, gridsize, cellsize)
    ''' apply governance from Layout
    '''
    if square: w, h = self.gridsize, self.gridsize

    ET.register_namespace('',"http://www.w3.org/2000/svg")
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 {w} {h}" 
      width="{w}{self.unit}" height="{h}{self.unit}"
      transform="scale({self.scale})"></svg>
    ''')
    comment = ET.Comment(
      f' scale:{scale} cellsize:{cellsize} gridsize:{gridsize} '
    )
    root.insert(0, comment)  # 0 is the index where comment is inserted
    if inkscape:             # add tags so plotter can split on layer
      ET.register_namespace(
        'inkscape',"http://www.inkscape.org/namespaces/inkscape"
      )
      root.set('xmlns:inkscape', "http://www.inkscape.org/namespaces/inkscape")
      self.ns1 = '{http://www.inkscape.org/namespaces/inkscape}'
    #ET.dump(root)
    self.ns = '{http://www.w3.org/2000/svg}'
    self.root = root
    self.inkscape = inkscape

  def make(self):
    ''' expand the doc from gridwalk and convert to XML
    '''
    #pp.pprint(self.doc)
    uniqid = 0 # xml elements must have unique IDs
    for group in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', group['style'])
      if self.inkscape:
        g.set('inkscape:groupmode', "layer") # need namespace for inkscape
        g.set('inkscape:label', self.trimStyle(group['style'])) # e.g "CCC"
      for s in group['shapes']:
        uniqid += 1
        name = s['name']
        #print(f"{name=} {str(uniqid)} {s.keys()=}")
        if name == 'circle':
          circle = ET.SubElement(g, f"{self.ns}circle", id=str(uniqid))
          circle.set('cx', f"{s['cx']:g}")
          circle.set('cy', f"{s['cy']:g}")
          circle.set('r', f"{s['r']:g}")
        #elif name == 'rect':
        elif name == 'square' or name == 'line':
          rect = ET.SubElement(g, f"{self.ns}rect", id=str(uniqid))
          rect.set("x", f"{s['x']:g}")
          rect.set("y", f"{s['y']:g}")
          rect.set("width", f"{s['width']:g}")
          rect.set("height", f"{s['height']:g}")
        #elif name == 'polygon':
        elif name == 'triangl' or name == 'diamond' or name == 'parabola':
          polyg = ET.SubElement(g, f"{self.ns}polygon", id=str(uniqid))
          polyg.set("points", s['points'])
        elif name == 'void':
          pass
        else:
          # pp.pprint(s)
          t = ET.SubElement(g, f"{self.ns}text", id=str(uniqid))
          t.text = name
          tx = s['x'] + 10
          ty = s['y'] + 30
          t.set("x", str(tx))
          t.set("y", str(ty))
          t.set("class", "{fill:#000;fill-opacity:1.0}")


  def write(self, svgfile):
    tree = ET.ElementTree(self.root)
    ET.indent(tree, level=0)
    tree.write(svgfile)

class LinearSvg(Svg):
  ''' output design to a two dimensional SVG that a plotter can understand
    clen = 15 blocksize = (6,2) scale = 2
    width = 15 * 6 * 2 height = 15 * 2 * 2

    viewbox "0 0 180 60" 
    width="180mm" height="60mm" 
    transform="scale(2)"
    super().__init__(unit='mm', scale=2, gridsize=max_blocksize, cellsize=15)
    super().__init__(
      unit='mm', scale=scale, gridsize=gridsize, cellsize=cellsize
    )
  '''

  def __init__(self, scale=1, clen=15):
    super().__init__(unit='mm', scale=scale, cellsize=clen)
    self.scale  = scale
    self.clen   = clen
    self.labels = list()

  def wireframe(self, blockOne, writeconf=False):
    ''' preview shapes generated by Flatten OR write meander.conf
    '''
    msg= self.writeMeanderConf(blockOne) if writeconf else self.markup(blockOne)
    return msg

  def cflatWireframe(self, block1, blocksz):
    ''' preview shapes generated by CellMaker.flatten
    '''
    w = self.clen * blocksz[0] * self.scale
    h = self.clen * blocksz[1] * self.scale
    super().__init__(
      unit='mm', scale=self.scale, gridsize=(w, h), cellsize=self.clen
    )
    inner_p = list()
    uniqid = 1 # xml elements must have unique IDs
    g      = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g.set('style', 'fill:#FFF;stroke:#000;stroke-width:1;fill-opacity:0.5')
    for pos, cell in block1.items():
      for layer in cell.bft:
        shape = layer.this
        if shape.name in ['invisible', 'void', 'multipolygon']:
          continue       # multi part geometry not expected here!
        uniqid += 1
        ''' SVG polygon
        '''
        p = ET.SubElement(g, f"{self.ns}polygon", id=str(uniqid))
        comment = ET.Comment( f' {layer.label} {shape.name}')
        points = str()
        #if shape.name == 'sqring' or shape.name == 'irregular':
        if shape.data.geom_type == 'Polygon': # Polygon with
          if len(shape.data.interiors):
            outer  = list(shape.data.exterior.coords)
            inner  = list(shape.data.interiors)
            coords = outer 
            [inner_p.append(list(lring.coords)) for lring in inner]
          else: 
            coords = list(shape.data.boundary.coords)
        else:
          coords = []
          print(f"ignoring {shape.data.geom_type}")
        for c in coords:
          coord = ','.join(map(str, c))
          points += f"{coord} "
        p.set("points", points.strip())
        p.insert(0, comment)  # 0 is the index where comment is inserted

    uniqid += 1
    g2 = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g2.set('style', 'fill:#FFF;stroke:#000;stroke-width:1;stroke-dasharray:0.5')
    for coords in inner_p:  
      uniqid += 1
      ''' Add any points from inner ring
      '''
      p = ET.SubElement(g2, f"{self.ns}polygon", id=str(uniqid))
      points = str()
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
      p.set("points", points.strip())

  def writeMeanderConf(self, done):
    ''' print to console an initial meander
    '''
    out = "meander:\n"
    for i in done:
      gmk = done[i]
      tx = gmk.shape.bounds[0]
      ty = gmk.shape.bounds[1]
      out += f"  {gmk.label}: N # {int(tx):>3},{int(ty):>3}\n"
    return out

  def make(self, model, blocks, meander_conf=dict()):
    self.doc = dict()     # reset for regrouping by fill
    for block in blocks:
      self.regroupColors(block, meander_conf=meander_conf)
      print('.', end='', flush=True)
    self.svgGroup()
    return f'tmp/{model}_mm.svg'

  def regroupColors(self, done, meander_conf):
    for i in done:
      gmk = done[i]
      xy  = gmk.meander.fill(conf=meander_conf, label=gmk.label)
      if xy.is_empty: # meander could not fill d
        continue
      if gmk.pencolor in self.doc:
        self.doc[gmk.pencolor].append(xy)
      else:
        self.doc[gmk.pencolor] = list()
        self.doc[gmk.pencolor].append(xy)

  def svgMarkup(self):
    ''' reset after wireframe
    '''
    uniqid = 0
    for content in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', content['style']) # swap fill for stroke
      for shape in content['shapes']:
        if shape['name'] == 'irregular': # square
          p = shape['points']
          #print(f"{p[:20]}")
        if shape['name'] == 'void': continue # empty group
        elif 'points' in shape: 
          uniqid += 1
          polyln = ET.SubElement(g, f"{self.ns}polyline", id=str(uniqid))
          polyln.set("points", shape['points'])
        else: print(f"hello new {shape['name']}")

  def svgGroup(self):
    ''' when pencolor is white it will not plot well on white paper
    but it is still allowed here

    plotters cannot fill, so style fill:none
    but they can draw lines, so polyline not polygon
    '''
    uniqid = 0
    for pencolor in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', f"fill:none;stroke:#{pencolor}")

      for line in self.doc[pencolor]:
        uniqid += 1
        points = str()
        for c in list(line.coords):
          x = c[0]
          y = c[1]
          points += f"{x},{y} "
        polyln = ET.SubElement(g, f"{self.ns}polyline", id=str(uniqid))
        polyln.set("style", 'stroke-width:0.5') # to show 1mm stripes in gthumb
        polyln.set("points", points)

'''
the
end
'''
