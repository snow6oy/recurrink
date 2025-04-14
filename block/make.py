#from cell.geomink import Geomink
from cell import Geomink, Cell, ShapelyCell

class GeoMaker:
  def __init__(self, scale=1.0, cellsize=60):
    self.scale    = scale
    self.cellsize = cellsize

  def make(self, blocksize, positions, cells):
    ''' given block and cell metadata make a geometry object 
        for each position on the block
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
      self.cellsize, scale=self.scale, coord=coord, 
      cell=cell, layer=layer, label=label
    )

  def makeCells(self, blocksize, positions, cells):
    ''' given block and cell metadata wrap geominks for each block position 
    '''
    block  = {}
    b0, b1 = blocksize
    for y in range(b1):
      for x in range(b0):
        coord  = (x, y)
        cn, tn = positions[coord]
        c      = Cell(cn, self.cellsize, coord, cells[cn])
        if tn in cells: c.addTop(tn, cells[tn])
        #print(coord, c.names)
        block[coord] = c
    return block

  def makeShapelyCells(self, blocksize, positions, cells):
    block  = {}
    b0, b1 = blocksize
    for y in range(b1):
      for x in range(b0):
        pos    = (x, y)
        cn, tn = positions[pos]
        cell   = ShapelyCell(pos, self.cellsize)
        cell.background(cn, cells[cn])
        cell.foreground(cn, cells[cn])
        if tn: cell.top(tn, cells[tn])
        #print(f"{cell.bft[0].label=} {len(cell.bft)=}")
        block[pos] = cell
    return block
'''
the
end
'''
