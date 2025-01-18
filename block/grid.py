'''
outfile.Layout.gridwalk
takes cells from db and returns svg.doc of hashes ordered by fill without cell details

outfile.Grid
takes cells from yaml and returns a blocki of Geominks ordered by grid also without cell details

this version will be the same as outfile.Grid but take cells from db and include cell details
'''
import pprint
from config import *
from cell.geomink import Geomink
from outfile import LinearSvg
from block.tmpfile import TmpFile

class Grid:
  scale = 1
  cellsize = 15

  def walk(self, blocksize, cells, positions):
    block  = []
    b0, b1  = blocksize
    for y in range(b1):
      for x in range(b0):
        coord = (x, y)
        c, t = positions[coord]
        # print(cells[c])
        for layer in ['top', 'fg', 'bg']:
          # print(f"{c=} {t=} {layer=}")
          if layer == 'top': 
            if t: block.append(self.getShape(t, coord, cells[t], layer='top'))
          else: block.append(self.getShape(c, coord, cells[c], layer=layer))
    return block

  def getShape(self, label, coord, cell, layer):
    '''
    print(label, layer)
    '''
    if cell['shape'] not in ['square', 'line']: 
      print(f"this {cell['shape']} is going to be interesting")
    shape = dict()
    x = int(coord[0] * self.cellsize)
    y = int(coord[1] * self.cellsize)
    gmk = Geomink(self.scale, self.cellsize)
    if layer == 'bg':
      bgcell = { 'facing': 'all', 'shape': 'square', 'size': 'medium', 'stroke_width': 0 }
      shape  = gmk.foreground(x, y, bgcell)
      fill   = cell['bg']
    else:
      shape = gmk.foreground(x, y, cell)
      fill  = cell['fill']
    x, y, w, h = list(shape.values())[:4]  # drop the name val cos we already know its square
    w += x
    h += y 
    gmk.set(xywh=(x, y, w, h), pencolor=fill, label=label)
    return gmk

class Model: 
  ''' to be installed as model.grid.walk
      class vars to be replaced once Layout() is parent
  '''
  scale    = 1.0
  gridsize = 270
  cellsize = 15

  def walk(self, block1, blocksize):
    blocks  = []
    b0, b1  = blocksize
    cellnum = round(self.gridsize / (self.cellsize * self.scale))
    grid_mm = int(cellnum * self.cellsize)
    x_block = int(b0 * self.cellsize)
    y_block = int(b1 * self.cellsize)
    print(f"{len(block1)=}")
    print(f"{blocksize=} {cellnum=} {grid_mm=} {self.cellsize=} {x_block=} {y_block=}")
    for y in range(0, grid_mm, y_block):
      for x in range(0, grid_mm, x_block):
        block = list()
        for cell in block1:
          a      = cell.shape, cell.pencolor
          clone  = Geomink(
            self.scale, self.cellsize, polygon=a[0], pencolor=a[1], label='R'
          ) # initial label
          clone.tx(x, y)
          block.append(clone)
          cb     = clone.shape.bounds
        blocks.append(block)
    return blocks

g       = Grid()
m       = Model()
tf      = TmpFile()
lsvg    = LinearSvg(scale=1, cellsize=15)
blocksz = (3,1)
block1  = g.walk(blocksz, config.cells, config.positions)

blox    = m.walk(block1, blocksz)
mc      = tf.modelConf('minkscape', 'meander')

'''
lsvg.wireframe(block1)
lsvg.write('tmp/grid_w.svg')
'''
lsvg.make(blox, meander_conf=mc)
lsvg.write('tmp/grid_m.svg')


