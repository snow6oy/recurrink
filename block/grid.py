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

class Grid:
  scale = 1
  cellsize = 30

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
      fill   = cell['fill']
    x, y, w, h = list(shape.values())[:4]  # drop the name val cos we already know its square
    w += x
    h += y 
    gmk.set(xywh=(x, y, w, h), pencolor=fill, label=label)
    return gmk

    '''
    block1  = [Geomink(c[:4], pencolor=c[-1]) for c in cells]
    grid_mm = int(self.cellnum * self.cellsize)
    blocks  = []
    print(f"{len(cells)=}")
    print(f"{blocksize=} {self.cellnum=} {grid_mm=} {self.cellsize=} {total_x=} {total_y=}")
    for x in range(0, grid_mm, total_x):
      for y in range(0, grid_mm, total_y):
        block = list()
        for cell in block1:
          a      = cell.shape, cell.pencolor
          clone  = Geomink(polygon=a[0], pencolor=a[1], label='R') # initial label
          clone.tx(x, y)
          block.append(clone)
          cb     = clone.shape.bounds
        blocks.append(block)
    return blocks
    '''

g       = Grid()
lsvg    = LinearSvg(scale=1, cellsize=30)
blocksz = (3,1)
block1  = g.walk(blocksz, config.cells, config.positions)

lsvg.wireframe(block1)
lsvg.write('tmp/grid.svg')
