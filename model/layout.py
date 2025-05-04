import copy
#from cell import Shapes

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
    if msg:
      raise ValueError(msg)
    gridsize      = gridsize if gridsize else self.governance[unit]['gridsize'] 
    cellsize      = cellsize if cellsize else self.governance[unit]['cellsize']
    self.unit     = unit
    self.scale    = float(scale)
    self.cellnum  = round(gridsize / (cellsize * scale))
    print(f"{self.cellnum=} {gridsize=} {cellsize=} {scale=}")
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
      # print(f"avoiding {cn=} {pos=} {li=} ")
      self.lgmk[li][cn] = list()
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
          shape  = gmk.svg(meander)  #, facing=gmk.facing)
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
'''
the
end
'''
