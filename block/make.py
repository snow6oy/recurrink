from cell.geomink import Geomink

class GeoMaker:
  # TODO set these with __init__ ?
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
    return Geomink(
      self.cellsize, scale=self.scale, coord=coord, cell=cell, layer=layer, label=label
    )
'''
the
end
'''
