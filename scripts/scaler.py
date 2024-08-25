import math
import pprint
pp = pprint.PrettyPrinter(indent = 2)
from config import *
''' python3 -m scripts.scaler
'''
class Points:
  ''' nw n ne    do the maths to render a cell
      w  c  e    points are calculated and called as p.ne p.nne p.s
      sw s se
  '''
  def __init__(self, x, y, stroke_width, size):
    self.n  = [x + size / 2,              y + stroke_width]
    self.e  = [x + size - stroke_width,   y + size / 2]
    self.s  = [x + size / 2,              y + size - stroke_width]
    self.w  = [x + stroke_width,          y + size / 2]
    self.ne = [x + size - stroke_width,   y + stroke_width] 
    self.se = [x + size - stroke_width,   y + size - stroke_width]
    self.nw = [x + stroke_width,          y + stroke_width]
    self.sw = [x + stroke_width,          y + size - stroke_width]
    self.mid= [x + size / 2,              y + size / 2]

class Layout():
  ''' expand cells and draw across grid
     9 * 60 = 540  * 2.0 = 1080
    12 * 60 = 720  * 1.5 = 1080
    18 * 60 = 1080 * 1.0 = 1080
    36 * 60 = 2160 * 0.5 = 1080
  '''

  def __init__(self, scale=1.0, gridsize=1080, cellsize=60):
    ''' scale expected to be one of [0.5, 1.0, 1.5, 2.0]
    '''
    self.scale = scale
    self.grid = round(gridsize / (cellsize * scale))
    self.cellsize = round(cellsize * scale)
    #self.checksum() 

    if False:           # run with gridpx=60 cellsize=6 to get a demo
      for col in range(self.grid):
        for row in range(self.grid):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()

  def gridwalk(self, blocksize, positions, cells):
    ''' traverse the grid once for each block, populating ET elems as we go
    '''
    self.cells = cells
    for i in self.cells:
      x = y = 0
      sw = self.cells[i]['stroke_width'] * self.scale
      p = Points(x, y, sw, self.cellsize)
      print(i, p.n)

  def cellsum(self):
    ''' like a checksum but for cells
    '''
    numoflayers = 3
    found = 0
    msg = None
    for s in self.doc:
      found += len(s['shapes']) 
      if True:
        '''
        for c in s['shapes']:
          print(c['width'], c['height'], c['x'], c['y'])
        '''
        print(len(s['shapes']), s['style'])

    cellnum = int((self.grid**2) * numoflayers)
    if (found != cellnum):
      msg = f"{cellnum} cells expected but found {found}"
    return msg

  def cube(self, cell, fill):
    ''' Slice a cell into nine cubes, each 20x20
        Example: cube({'name': 'rect', 'x': '120', 'y': '120', 'width': '60', 'height': '60'})
    '''
    x = round(float(cell['x'])) # TODO ask Layout to send integers
    y = round(float(cell['y']))
    w = round(float(cell['width']))
    h = round(float(cell['height']))
    #print(f"{x:>4}, {y:<4} {w}x{h} {fill}")
    for Y in range(y, (h + y), self.cubesz):
      for X in range(x, (w + x), self.cubesz):
        moveto = tuple([X, Y])
        self.gcdata[moveto] = fill # top overwrites fg which overwrites bg

# cellsize / 3 must be a whole number
# x,y must comply with paper size e.g. A4 = 210x297 mm
# scale must in range
# strokes must scale

# cell width height must be > 0
# ?? blocksize cannot exceed grid
if __name__ == '__main__':
  ''' expand cells and draw across grid
     9 * 60 = 540  * 2.0 = 1080
    12 * 60 = 720  * 1.5 = 1080
    18 * 60 = 1080 * 1.0 = 1080
    36 * 60 = 2160 * 0.5 = 1080

                   gridsz cellsz maxmm
    a4 210x297 mm     180     24   210
    a3 297x420 mm     270     36   297
    a3                720     60   980  above * 3.3 
  '''
  scale_range = [0.5, 1.0, 1.5, 2.0]
  test_vals = [ (1080, 60, 1081, 5), (720, 60, 980, 0) ]
  # (270, 36, 297, 0) ]

  blocksize = 24  # afroclave[x] = 24
  print("\t".join(['scale', "num_cel", "cel_siz", "scal_ok", "div_3", "blocksz", "hi_wid", "fit_pg", "strok_w", "N_x"]))
  print('.' * 80)
  for scale in [0.5, 1.0, 1.5, 2.0, 2.9]:
    for tv in test_vals:
      lt = Layout(scale=scale, gridsize=tv[0], cellsize=tv[1])
      max_len = tv[2]
      hw = lt.grid * lt.cellsize
      div_3 = 'no' if (lt.cellsize % 3) else 'yes'
      sw = tv[3] * scale
      p = Points(0, 0, sw, lt.cellsize) 
      print("\t".join([
        str(lt.scale), 
        str(lt.grid), 
        str(lt.cellsize), 
        str(scale in scale_range), 
        div_3,
        str(blocksize <= lt.grid),
        str(hw), 
        str((hw < max_len)),
        str(sw),
        str(p.n[0])
      ]))
    print('.' * 80)
