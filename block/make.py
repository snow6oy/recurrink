from shapely.geometry import Polygon, LineString
from cell import Layer
from .meander import Meander
from .styles import Styles

class Make:

  VERBOSE = False
  BLOCKSZ = (3, 1)
  CLEN    = 6

  def __init__(self): 
    self.cells = dict()
    self.style = Styles()
    self.guide = dict()

  def walk(self, positions, cells):
    ''' navigate the model and populate cells
    '''
    self.setBlocksize(positions)
    for pos in positions:
      cell = Layer(clen=self.CLEN, pos=pos)
      cell.background()
      label = positions[pos][0]
      self.style.add(pos, fill=cells[label]['bg'])

      for label in positions[pos]:
        if not label: continue
        if bool(cells[label]['top']):
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, fill=cells[label]['fill'])
        else:
          cell.foreground(
            shape  = cells[label]['shape'],
            facing = cells[label]['facing'],
            size   = cells[label]['size']
          )
          self.style.add(pos, fill=cells[label]['fill'])
      self.cells[pos] = cell.polygon()
      self.guide[pos] = cell.direction

  def meander(self, padding=True):
    ''' transform polygons into lines
    '''
    for z in range(3): # bg 0 fg 1 top 2
      for pos, c in self.cells.items():

        if z == 2 and len(c.interiors) > 1: 
          lring = c.interiors[1]                   # top
        elif z == 2: continue 
        elif z == 1: lring = c.interiors[0]        # fg
        elif z == 0: lring = c.exterior            # bg

        if self.VERBOSE:
          print(f"{z} {pos} {len(c.interiors)} {self.direction[pos]}")

        m     = Meander(Polygon(lring))
        guide = self.guide[pos][z]
        shape = m.pad() if padding else m.shape
        gline = m.guidelines(shape, guide)  # ('EB', 'ET'))
        pt, e = m.collectPoints(shape, gline)

        ''' replace the guide tuple with a Shapely.LineString
        '''
        if e: raise ValueError(e)
        else: self.guide[pos][z] = LineString(m.makeStripes(pt))

  def setBlocksize(self, positions):
    ''' extract blocksize and set for downstream functions
    '''
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

'''
the
end
'''
