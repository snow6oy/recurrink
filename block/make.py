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
'''
the
end
'''
