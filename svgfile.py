#!/usr/bin/env python3

import re
import pprint
import inkex
import math
import os.path
from inkex import Group, Circle, Rectangle, Polygon, TextElement
from db import Cells, Blocks, Models
pp = pprint.PrettyPrinter(indent=2)

#from recurrink import TmpFile
# from inkex import Group, load_svg
# from svgfile import Layout
# from db import Blocks, Models

class Draw:
  ''' do the maths to render a cell
  '''
  def __init__(self, baseUnit):
    ''' units must be in sync with Layout.sizeUu 
    '''
    self.sizeUu  = baseUnit[0] # size
    self.x_offset = baseUnit[1] # x offset
    self.y_offset = baseUnit[2] # y offset

  def backgrounds(self, cell, x, y):
    ''' the first cell painted onto the grid is a filled rectangle
        see Builder for a list of the available colours
    '''
    w = str(self.sizeUu)
    h = str(self.sizeUu)
    bg = Rectangle(x=str(x), y=str(y), width=w, height=h)
    return bg

  def shape(self, cell, X, Y, a):
    ''' create a shape from a cell for adding to a group
    '''
    self.hw = a['stroke_width'] / 2  # stroke width is halved for repositioning
    self.fw = a['stroke_width']      # full width
    if a['shape'] == 'circle':
      s = self.circle(cell, X, Y, a)
    elif a['shape'] == 'line':
      s = self.line(cell, X, Y, a)
    elif a['shape'] == 'square':
      s = self.square(cell, X, Y, a)
    elif a['shape'] == 'triangle':
      s = self.triangle(cell, X, Y, a)
    elif a['shape'] == 'diamond':
      s = self.diamond(cell, X, Y, a)
    else:
      s = self.set_text(a['shape'], X, Y)
    return s

  def circle(self, cell, X, Y, a):
    if a['size'] == 'large': 
      size = self.sizeUu / 2
      sum_two_sides = (size**2 + size**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - self.hw
    elif a['size'] == 'medium':
      r = (self.sizeUu / 2 - self.hw) # normal size
    else:
      raise ValueError(f"Cannot set circle <{cell}> to {a['size']} size")
    x = str(X + self.sizeUu / 2)
    y = str(Y + self.sizeUu / 2)
    circle = Circle(cx=x, cy=y, r=str(r))
    return circle

  def line(self, cell, X, Y, a):
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    a['facing'] = 'north' if a['facing'] == 'south' else a['facing']
    a['facing'] = 'east' if a['facing'] == 'west' else a['facing']
    if a['size'] == 'large' and a['facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + self.hw)
      y      = str(Y - self.sizeUu / 3 + self.hw)
      width  = str(self.sizeUu / 3 - self.fw)
      height = str((self.sizeUu / 3 * 2 + self.sizeUu) - self.fw)
    elif a['size'] == 'large' and a['facing'] == 'east':
      x      = str(X - self.sizeUu / 3 + self.hw)
      y      = str(Y + self.sizeUu / 3 + self.hw)
      width  = str((self.sizeUu / 3 * 2 + self.sizeUu) - self.fw)
      height = str(self.sizeUu / 3 - self.fw)
    elif a['size'] == 'medium' and a['facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + self.hw)
      y      = str(Y + self.hw)
      width  = str(self.sizeUu / 3 - self.fw)
      height = str(self.sizeUu - self.fw)
    elif a['size'] == 'medium' and a['facing'] == 'east':
      x      = str(X + self.hw)
      y      = str(Y + self.sizeUu / 3 + self.hw)
      width  = str(self.sizeUu - self.fw)
      height = str(self.sizeUu / 3 - self.fw)
    else:
      raise ValueError(f"Cannot set {cell} to {a['size']}")
    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def square(self, cell, xSizeMm, ySizeMm, a):
    if a['size'] == 'medium':
      x      = str(xSizeMm + self.hw)
      y      = str(ySizeMm + self.hw)
      width  = str(self.sizeUu - self.fw)
      height = str(self.sizeUu - self.fw)
    elif a['size'] == 'large':
      third  = self.sizeUu / 3
      x      = str(xSizeMm - third / 2 + self.hw)
      y      = str(ySizeMm - third / 2 + self.hw)
      width  = str(self.sizeUu + third - self.fw)
      height = str(self.sizeUu + third - self.fw)
    else:
      raise ValueError("Cannot set rectangle {}".format(cell))
    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def triangle(self, cell, X, Y, a):
    x = [ 
      X + self.fw,
      X + self.hw,
      X + self.sizeUu - self.hw,
      X + self.sizeUu - self.fw, 
      X + self.sizeUu / 2,
      X + self.sizeUu / 2 + self.hw,
      X + self.sizeUu / 2 - self.hw,
    ]
    y = [
      Y + self.fw, 
      Y + self.sizeUu / 2, 
      Y + self.sizeUu - self.fw,
      Y + self.sizeUu / 2 + self.hw, 
      Y + self.sizeUu / 2 - self.hw,
      Y + self.hw
    ]
    if a['facing'] == 'west': 
      points = [ x[0], y[1], x[2], y[1], x[2], y[2], x[0], y[1] ]
    elif a['facing'] == 'east': 
      points = [ x[1], y[0], x[3], y[1], x[1], y[2], x[1], y[0] ]
    elif a['facing'] == 'north': 
      points = [ x[0], y[4], x[4], y[0], x[3], y[4], x[0], y[4] ]
    elif a['facing'] == 'south':
      points = [ x[1], y[5], x[4], y[2], x[2], y[5], x[1], y[5] ]
    else:
      raise ValueError("Cannot face triangle {}".format(a['facing']))
    polyg = Polygon(points=",".join(map(str, points)))
    return polyg
    ''' south
        X + self.hw, Y + self.hw, 
        X + self.sizeUu / 2, Y + self.sizeUu - self.fw, 
        X + self.sizeUu - self.hw, Y + self.hw,
        X + self.hw, Y + self.hw
      north
        X + self.fw, Y + self.sizeUu - self.hw,
        X + self.sizeUu / 2, Y + self.fw,
        X + self.sizeUu - self.fw, Y + self.sizeUu - self.hw,
        X + self.fw, Y + self.sizeUu - self.hw
      west
        X + self.fw, Y + self.sizeUu / 2, 
        X + self.sizeUu - self.hw, Y + self.fw, 
        X + self.sizeUu - self.hw, Y + self.sizeUu - self.fw,
        X + self.fw, Y + self.sizeUu / 2
      east
        X + self.hw, Y + self.fw, 
        X + self.sizeUu - self.fw, Y + self.sizeUu / 2,
        X + self.hw, Y + self.sizeUu - self.fw,
        X + self.hw, Y + self.fw
    '''
  
  def diamond(self, cell, X, Y, a):
    x = [ 
      X + self.fw,
      X + self.hw,
      X + self.sizeUu - self.hw,
      X + self.sizeUu - self.fw, 
      X + self.sizeUu / 2,
      X + self.sizeUu / 2 + self.hw,
      X + self.sizeUu / 2 - self.hw,
    ]
    y = [
      Y + self.fw, 
      Y + self.sizeUu / 2, 
      Y + self.sizeUu - self.fw,
      Y + self.sizeUu / 2 + self.hw, 
      Y + self.sizeUu / 2 - self.hw
    ]
    if a['facing'] == 'all': 
      points = [ x[0], y[1], x[4], y[0], x[3], y[1], x[4], y[2], x[0], y[1] ]
    elif a['facing'] == 'west': 
      points = [ x[0], y[1], x[6], y[0], x[6], y[2], x[0], y[1] ]
    elif a['facing'] == 'east': 
      points = [ x[5], y[0], x[3], y[1], x[5], y[2], x[5], y[0] ]
    elif a['facing'] == 'north': 
      points = [ x[0], y[4], x[4], y[0], x[3], y[4], x[0], y[4] ]
    elif a['facing'] == 'south':
      points = [ x[0], y[3], x[4], y[2], x[2], y[3], x[0], y[3] ]
    else:
      raise ValueError(f"Cannot face diamond {a['facing']}")
    polyg = Polygon(points=",".join(map(str, points)))
    return polyg
  
  def set_text(self, shape, X, Y):
    ''' when the shape is unknown print as text in the cell
    '''
    x = str(X + 3)
    y = str(Y + 40)
    textElement = TextElement(x=x, y=y)
    textElement.text = shape
    # self.debug(textElement)
    return textElement

class Layout(Draw):
  ''' expand cells provided by Draw across a canvas
  '''
  def __init__(self, model, control):
    ''' 
    original calculation was page size 210 x 297 mm (A4 portrait)
    since unit are not millimeters this table is inaccurate

    factor    size   col  row   x os   y os
      0.5     24.0     7   11   21.0   16.5  twice as big
      1.0     12.0    15   22   15.0   16.5  do nothing
      2.0      6.0    30   44   15.0   16.5  half size
    '''
    self.b = Blocks(model)
    self.c = Cells()
    self.model = model
    self.create(control)
    self.width   = 1122.5197  # px
    self.height  = 793.70081
    self.size    = (48 / self.factor)  
    self.maxCols = int(22 * self.factor)
    self.maxRows = int(15 * self.factor)  # num of row  
    numOfMargins = 2
    self.xOffset = (self.width  - (self.maxCols * self.size)) / numOfMargins # 33.25985000000003
    self.yOffset = (self.height - (self.maxRows * self.size)) / numOfMargins # 36.85040500000002
    super().__init__([self.size, self.xOffset, self.yOffset])

  def create(self, control):
    ''' convert a two digit control code into a float for scaling
        0 is default
        odd numbers zoom out
        even numbers zoom in
    '''
    # = int(list(control)[0])
    f, c = list(control)
    scale = [1.0, 1.1, 0.9, 1.3, 0.8, 1.5, 0.7, 1.8, 0.5, 2.0]
    self.factor = scale[int(f)]
    self.control = int(c)

  def transform(self, cells):
    self.cells = self.c.update(cells, self.control)

  def get_cell_by_position(self, pos):
    '''
    repeat the block to fit the canvas
    1. calculate the block number using integer division, blocksize and counter
    2. then new counter = counter - blocknumber * blocksize
    '''
    x, y = pos[0], pos[1]
    #b = Blocks(self.model)
    m = Models()
    cell = None
    positions = self.b.get() 
    blocksize = m.get(model=self.model)[2]
    (x_blocksize, y_blocksize) = blocksize
    y_blocknum = int(y / y_blocksize)
    Y = y - (y_blocknum * y_blocksize)
    x_blocknum = int(x / x_blocksize)
    X = x - (x_blocknum * x_blocksize)
    #print(f'xy({x}, {y})  XY({X}, {Y})  blocknum({x_blocknum}, {y_blocknum})')
    current_posn = (X, Y) # tuples are immutable
    return positions[current_posn]

  # def blocknum_to_uu(self, xBlocknum, yBlocknum):
  def blocknum_to_uu(self, pos):
    ''' convert a position in the grid to pixels 
    '''
    xBlocknum, yBlocknum = pos[0], pos[1]
    xUu = self.xOffset + (xBlocknum * self.size)
    yUu = self.yOffset + (yBlocknum * self.size)
    return xUu, yUu

  def render(self, group):
    ''' draw out a model by repeating blocks across the canvas
    '''
    for paintOrder in range(2):
      for y in range(self.maxRows):
        print('.', end='', flush=True)
        for x in range(self.maxCols):
          pos = tuple([x, y])
          (xSizeMm, ySizeMm) = self.blocknum_to_uu(pos)
          cell = self.get_cell_by_position(pos)
          #data = cells[cell]
          data = self.cells[cell]
          if not data:
            continue # checker-board background !
          gid = f"{cell}{paintOrder}"
          sid = f"{cell}{paintOrder}-{x}-{y}"
          if paintOrder:
            shape = self.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method here
            group[gid].add(shape) 
          else:
            shape = self.backgrounds(cell, xSizeMm, ySizeMm)
            shape.set_id(sid)    # calling an inkex method
            group[gid].add(shape)
    return None

  def build(self, svg):
    ''' Generate inkex groups for the svg renderer to use  
    '''
    #cells = self.tf.read(self.model, txt=data) # convert string to dict
    groups_to_create = self.b.cells()
    group = {}  # hold a local reference to groups created in svg doc
    stroke_width = {}
    sw0 = svg.unittouu(0) # hide the cracks between the background tiles
    for g in groups_to_create:
      # draw background  cells
      bg = Group()
      bg.set_id(f'{g}0')
      #bg.style = { 'fill' : cells[g]['bg'], 'stroke-width': sw0, 'stroke':'#fff' }
      bg.style = { 'fill' : self.cells[g]['bg'], 'stroke-width': sw0, 'stroke':'#fff' }
      group[f'{g}0'] = bg # local copy
      svg.add(bg)
      # draw foreground cells
      fg = Group()
      sw1 = svg.unittouu(self.cells[g]['stroke_width'])
      fg.set_id(f'{g}1') 
      fg.style = {
        'fill'            : self.cells[g]['fill'],
        'fill-opacity'    : self.cells[g]['fill_opacity'],
        'stroke'          : self.cells[g]['stroke'],
        'stroke-width'    : sw1,
        'stroke-dasharray': self.cells[g]['stroke_dasharray'],
        'stroke-opacity'  : self.cells[g]['stroke_opacity']
      }
      group[f'{g}1'] = fg
      # TODO what is stroke width used for ?
      stroke_width[f'{g}1'] = sw1  # adjust cell dimension according to stroke width
      svg.add(fg)
    return group
