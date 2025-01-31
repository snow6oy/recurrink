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
    ''' create a geometry object from cell data
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

if __name__ == 'main':
  g       = Grid()
  m       = Models()
  nm      = NewModel() # TODO newmodel moved to model already ..
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

'''
the
end
'''
