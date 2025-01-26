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
from model.svg import LinearSvg
from block import TmpFile
from model.data import ModelData # old model for metadata

class GeoMaker:
  scale = 1.0
  cellsize = 15

  def make(self, blocksize, positions, cells):
    ''' given block and cell metadata make a geometry object for each position on the block
    '''
    block  = []
    b0, b1  = blocksize
    for y in range(b1):
      for x in range(b0):
        coord = (x, y)
        c, t = positions[coord]
        #print(cells[c])
        for layer in ['top', 'fg', 'bg']:
          #print(f"{c=} {t=} {layer=}")
          if layer == 'top': 
            if t: block.append(self.getShape(t, coord, cells[t], layer='top'))
          else: block.append(self.getShape(c, coord, cells[c], layer=layer))
    return block

  def getShape(self, label, coord, cell, layer):
    '''
    print(label, layer)
      shape  = gmk.foreground(x, y, bgcell)
    shape = dict()
    bgcell = { 'facing': 'all', 'shape': 'square', 'size': 'medium', 'stroke_width': 0 }
    else:
      shape = gmk.foreground(x, y, cell)
      gmk = Geomink(self.cellsize, scale=self.scale, xywh=(x, y, w, h), pencolor=fill, label=label)
    x, y, w, h = list(shape.values())[:4]  # drop the name val cos we already know its square
    w += x
    h += y
    '''
    x = int(coord[0] * self.cellsize)
    y = int(coord[1] * self.cellsize)
    if cell['shape'] not in ['square', 'line']: 
      print(f"this {cell['shape']} is going to be interesting")
    fill = cell['bg'] if layer == 'bg' else cell['fill']
    if list(fill)[0] == '#': fill = fill[1:]
    return Geomink(
      self.cellsize, scale=self.scale, coord=(x, y), cell=cell, 
      layer=layer, pencolor=fill, label=label
    )

class NewModel: 
  ''' to be installed as model.grid.walk
      class vars to be replaced once Layout() is parent
  '''
  scale    = 1.0
  gridsize = 270
  cellsize = 15

  def walk(self, blocksize, block1):
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

if __name__ == 'main':
  g       = Grid()
  m       = Models()
  nm      = NewModel()
  tf      = TmpFile()
  lsvg    = LinearSvg(scale=1, cellsize=15)
  models  = ['eflat', 'sonny', 'koto', 'buleria', 'minkscape']
  test_case = 0
  model   = models[test_case]

  if model == 'minkscape':
    blocksz = (3,1)
    block1  = g.walk(blocksz, config.cells, config.positions)
  else:
    blocksz   = m.read(model=model)[2] # can get scale too
    positions = m.read_positions(model)
    cells     = tf.read(model, output=dict())
    block1    = g.walk(blocksz, cells, positions)
  
  blox    = nm.walk(block1, blocksz)
  mc      = tf.modelConf(model, 'meander')
  
  if False:
    lsvg.wireframe(block1)
    lsvg.write('tmp/grid_w.svg')
  else:
    lsvg.make(blox, meander_conf=mc)
    lsvg.write('tmp/grid_m.svg')

