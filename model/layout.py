import copy
from cell import Shapes

class Layout():
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
    if msg:
      raise ValueError(msg)
    gridsize      = gridsize if gridsize else self.governance[unit]['gridsize'] 
    cellsize      = cellsize if cellsize else self.governance[unit]['cellsize']
    self.unit     = unit
    self.scale    = float(scale)
    self.cellnum  = round(gridsize / (cellsize * scale))
    #print(f"{self.cellnum=} {gridsize=} {cellsize=} {scale=}")
    self.cellsize = round(cellsize * scale)
    self.gridsize = gridsize
    self.styles   = dict() # unique style associated with many cells
    self.lstyles  = [{} for _ in range(3)] # unique style for each layer
    self.lgmk     = [{} for _ in range(3)] # unique gmk   for each layer
    self.seen     = str()    # have we seen this style before
    self.doc      = list()
    self.shapes   = Shapes(self.scale, self.cellsize)
    if False:           # run with gridsize=60 cellsize=6 to get a demo
      for col in range(self.cellnum):
        for row in range(self.cellnum):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()

  def gridwalk(self, blocksize, positions, cells):
    ''' traverse the grid once for each block, populating ET elems as we go
    '''
    self.cells = cells
    self.blocksize = blocksize         # pass blocksize to LinearSvg()
    for layer in ['bg', 'fg', 'top']:
      for cell in self.cells:
        self.uniqstyle(cell, layer, self.cells[cell]['top'],
          bg=self.cells[cell]['bg'],
          fill=self.cells[cell]['fill'],
          fo=self.cells[cell]['fill_opacity'],
          stroke=self.cells[cell]['stroke'],
          sd=self.cells[cell]['stroke_dasharray'],
          so=self.cells[cell]['stroke_opacity'],
          sw=self.cells[cell]['stroke_width']
        )
      for cell in self.cells:
        for gy in range(0, self.cellnum, blocksize[1]):
          for gx in range(0, self.cellnum, blocksize[0]):
            for y in range(blocksize[1]):
              for x in range(blocksize[0]):
                pos = tuple([x, y])
                c, t = positions[pos] # cell, top
                self.rendercell(layer, cell, c, t, gx, x, gy, y)
      self.styles.clear() # empty self.styles before next layer

  def getgroup(self, layer, cell):
    ''' combine style and counter to make a group
    '''
    style = self.findstyle(cell) 
    if style != self.seen:
      self.seen = style # HINT use python set() instead of self.seen
      self.doc.append({ 'style': style, 'shapes': list() })
    return self.doc[-1]['shapes']

  def rendercell(self, layer, cell, c, t, gx, x, gy, y):
    ''' gather inputs call Shapes() and add shape to group
    '''
    X = (gx + x) * self.cellsize # this logic is the base for Points
    Y = (gy + y) * self.cellsize
    if layer == 'bg' and cell == c:
      g = self.getgroup('bg', cell)
      bgcell = { 'facing': 'all', 'shape': 'square', 'size': 'medium', 'stroke_width': 0 }
      g.append(self.shapes.foreground(X, Y, bgcell))
    if layer == 'fg' and cell == c:
      if ord(cell) < 97:  # upper case
        self.cells[cell]['shape'] = ' '.join([c, self.cells[cell]['shape']]) # testcard hack
      g = self.getgroup('fg', cell)
      g.append(self.shapes.foreground(X, Y, self.cells[cell]))
    if layer == 'top' and cell == t and self.cells[cell]['top']:
      g = self.getgroup('top', cell)
      g.append(self.shapes.foreground(X, Y, self.cells[cell]))

  def uniqstyle(self, cell, layer, top, bg=None, fill=None, fo=1, stroke=None, sw=0, sd=0, so=1):
    ''' remember what style to use for this cell and that layer
        as None is invalid XML we use 0 as default for: fo sw sd so
    '''
    if bg is None and fill is None:
      raise ValueError(f"either {bg} or {fill} are empty")
    style = str()
    if layer == 'bg': # create new entry in self.layers.bg
      style = f"fill:{bg};stroke-width:0" # hide the cracks between the background tiles
    elif layer == 'fg' and sw: # and not top:
      style = f"fill:{fill};fill-opacity:{fo};stroke:{stroke};stroke-width:{sw};stroke-dasharray:{sd};stroke-opacity:{so}"
    elif layer == 'fg': # and not top:
      style = f"fill:{fill};fill-opacity:{fo}"
    elif layer == 'top' and top and sw:
      style = f"fill:{fill};fill-opacity:{fo};stroke:{stroke};stroke-width:{sw};stroke-dasharray:{sd};stroke-opacity:{so}"
    elif layer == 'top' and top:
      style = f"fill:{fill};fill-opacity:{fo}"

    if style and style in self.styles:
      self.styles[style].append(cell)
    elif style:
      self.styles[style] = list()
      self.styles[style].append(cell)

  def findstyle(self, cell):
    ''' find a style saved in uniqstyle
    '''
    found = None
    for s in self.styles:
      if cell in self.styles[s]:
        found = s
        break
    if not found: 
      raise ValueError(f"{cell} aint got no style (hint: cannot make bg for topcell?)")
    return found

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
  def styleGuide(self, block1):
    ''' create a dict of styles:[cellnames]
        that are unique within each layer
        l0: a:s1 b: s2
        l1: a:s1 c: s3
    '''
    for pos in block1:
      cell = block1[pos]
      for li in range(len(cell.bft)): # li layer index
        self.addStyle(cell.getStyle(li), cell.names[li], li)
    #print(self.lstyles[2]['c'])

  def addStyle(self, style, name, layer):
    ''' group geometries in SVG
        styles are unique for each layer 
    '''
    self.lstyles[layer][name] = style

  def __gridWalk(self, blocksize, positions, block1):
    ''' traverse the grid once for each block, populating ET elems as we go
    '''
    self.blocksize = blocksize # pass blocksize to LinearSvg()
    for li in range(3):
      for pos in block1:
        cell = block1[pos]
        if len(cell.bft) == li: continue # topless (.)(.)
        name = cell.names[li]
        style = self.lstyles[li][name]
        print(f"{name=} {style=} {cell.bft[li].layer=}")

  def gridWalk(self, blocksize, block1):
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
        xy   = tuple([row, col])
        cell = block1[xy]
        self.addGeomink(0, XY, cell.names[0], cell.bft[0]) # background
        self.addGeomink(1, XY, cell.names[1], cell.bft[1]) # foreground
        if len(cell.bft) == 2: continue # topless (.)(.) 
        self.addGeomink(2, XY, cell.names[2], cell.bft[2]) # top

  def addGeomink(self, layer, pos, name, gmk):
    ''' clone geominks then stash by layer and name
    '''
    clone  = copy.copy(gmk)
    clone.tx(pos[0], pos[1])
    #print(f"{clone.shape.bounds} {pos=}")
    if name in self.lgmk[layer]:
      self.lgmk[layer][name].append(clone)
    else:
      self.lgmk[layer][name] = list()
      self.lgmk[layer][name].append(clone)

  def __svgDoc(self):
    ''' pull objects from self and construct inputs to Svg()
        [ { shapes: [ {} {} ], style: fill:#00F } ]
    '''
    keys = ['width', 'height', 'x', 'y', 'name']
    sdoc = list()
    di   = 0      # doc index
    for li in range(3):               # layer index
      seen = dict()                   # uniq style
      for cn in self.lgmk[li]:        # cell names in layer
        style = self.lstyles[li][cn]
        if style not in seen:
          seen[style] = di
          sdoc.append(dict())
          sdoc[di]['shapes'] = list()
          sdoc[di]['style']  = style
          di += 1
        dj = seen[style]
        for gmk in self.lgmk[li][cn]:
          x, y, W, H = gmk.shape.bounds
          w = W - x
          h = H - y
          #print(f"layer {li} {w=} {h=} {x=} {y=}")
          shape = dict(zip(keys, [w, h, x, y, gmk.name]))
          sdoc[dj]['shapes'].append(shape)
    self.doc = sdoc

  def svgDoc(self, legacy=False):
    ''' pull objects from self and construct inputs to Svg()
        [ { shapes: [ {} {} ], style: fill:#00F } ]
    '''
    keys = ['width', 'height', 'x', 'y', 'name']
    sdoc = list()
    di   = 0      # doc index
    for li in range(3):               # layer index
      seen = dict()                   # uniq style
      for cn in self.lgmk[li]:        # cell names in layer
	#print(cn)
        style = self.lstyles[li][cn]
        if style not in seen:
          seen[style] = di
          sdoc.append(dict())
          sdoc[di]['shapes'] = list()
          sdoc[di]['style']  = style
          di += 1
        dj = seen[style]
        # TODO decouple lgmk from Shapely 
        for gmk in self.lgmk[li][cn]:
          shape = gmk.getShape(legacy)
          sdoc[dj]['shapes'].append(shape)
          '''
          x, y, W, H = gmk.shape.bounds
          w = W - x
          h = H - y
          #print(f"layer {li} {w=} {h=} {x=} {y=}")
          shape = dict(zip(keys, [w, h, x, y, gmk.name]))
          '''
    self.doc = sdoc

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

  '''
  def _walk(self, blocksize, cells):
    block1  = [Geomink(
    self.cellsize, scale=self.scale, xywh=c[:4], pencolor=c[-1]) for c in cells]
    b0, b1  = blocksize
    total_x = int(b0 * self.cellsize)
    total_y = int(b1 * self.cellsize)
    grid_mm = int(self.cellnum * self.cellsize)
    blocks  = []
    print(f"{len(cells)=}")
    print(f"{blocksize=} {self.cellnum=} {grid_mm=} {self.cellsize=} {total_x=} {total_y=}")
    for x in range(0, grid_mm, total_x):
      for y in range(0, grid_mm, total_y):
        block = list()
        for cell in block1:
          a      = cell.shape, cell.pencolor
          clone  = Geomink(
            self.cellsize, scale=self.scale, 
            polygon=a[0], pencolor=a[1], label='R'
          ) # initial label
          clone.tx(x, y)
          block.append(clone)
          cb     = clone.shape.bounds
        blocks.append(block)
    return blocks
  '''

'''
the
end
'''
