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
  ''' the below cell sizes were calculated as
      gridsize / scale / cellnum
      18 was chosen as the preferred number of cells
      for both column and row with scale 1
      the num of cells is gridsize / cellsize

 	PIXELS

	num of	cell   	       grid
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
            30 *    9    * 0.6 =  270
  '''

  def __init__(self, unit='px', scale=1.0, gridsize=None, cellsize=None):
    ''' scale expected to be one of [0.5, 1.0, 1.5, 2.0]
    '''
    self.governance = {
      'mm': { 'gridsize':270,  'cellsize':15, 'scale': [0.6, 1.0, 2.0] },
      'px': { 'gridsize':1080, 'cellsize':60, 'scale': [0.5, 0.75, 1.0, 1.5, 2.0] }
    }
    gridsize      = gridsize if gridsize else self.governance[unit]['gridsize']
    cellsize      = cellsize if cellsize else self.governance[unit]['cellsize']
    self.unit     = unit
    self.scale    = scale
    self.cellnum  = round(gridsize / (cellsize * scale))
    self.cellsize = round(cellsize * scale)
    errmsg = self.checksum(unit, gridsize, cellsize)
    if errmsg:
      raise ValueError(errmsg)

    if False: # run with gridsize=18 cellsize=3 to get a demo
      for col in range(self.cellnum):
        for row in range(self.cellnum):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()

  def checksum(self, unit, gridsize, cellsize):
    ''' sanity check the inputs
    '''
    if self.unit not in list(self.governance.keys()):
      return f'checksum failed: unknown unit {self.unit}'
    elif self.scale not in self.governance[unit]['scale']: # scale must in range
      return f'checksum failed scale {self.scale}'
    elif (self.cellsize % 3): # cellsize / 3 must be a whole number
      return f'checksum failed cell size div by three {self.cellsize}'
    else:
      return None

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

    cellnum = int((self.cellnum**2) * numoflayers)
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

def inputPrinter(u, scale_vals, tv):
  blockcount = 24  # afroclave has 24 cells in a single block
  print('.' * 80)
  print(f"UNITS = {u}")
  print("\t".join([
    'scale', "cellnum", "cellsz ", "scal_ok", "div_3", "max_blc", 
    "bloc_fq", "fit_pg", "strok_w", "N_x"
  ]))
  print('.' * 80)
  for scale in scale_vals:
    lt = Layout(unit=u, scale=scale, gridsize=tv[0], cellsize=tv[1])
    max_len = tv[2]
    hw = lt.cellnum * lt.cellsize
    div_3 = 'no' if (lt.cellsize % 3) else 'yes'
    sw = tv[3] * scale
    p = Points(0, 0, sw, lt.cellsize) 
    print("\t".join([
      str(lt.scale), 
      str(lt.cellnum), 
      str(lt.cellsize), 
      str(scale in scale_range), 
      div_3,
      str(blockcount <= lt.cellnum),
      str(hw), 
      str((hw < max_len)),
      str(sw),
      str(p.n[0])
    ]))

if __name__ == '__main__':
  if False:
    ''' calculate cell and grid sizes by scale and unit
    '''
    scale_range = [0.5, 0.75, 1.0, 1.5, 2.0]
    tv = (1080, 60, 1081, 5)
    inputPrinter('px', scale_range, tv)
  
    scale_range = [0.6, 1.0, 2.0]
    tv = (270, 15, 297, 0)
    inputPrinter('mm', scale_range, tv)
  else:
   lt = Layout(gridsize=18, cellsize=3)
