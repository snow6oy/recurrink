#!/usr/bin/env python3

import re
import pprint
import inkex
import math
import os.path
from inkex import Group, Circle, Rectangle, Polygon, TextElement
from db import Cells, Blocks, Models
pp = pprint.PrettyPrinter(indent=2)


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

class Draw:
  ''' create a shape for the required position
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
    p = Points(X, Y, a['stroke_width'], self.sizeUu)

    if ord(cell) < 97:  # upper case
      s = self.set_text(a['shape'], X, Y)
    elif a['shape'] == 'circle':
      s = self.circle(a['size'], a['stroke_width'], p)
    elif a['shape'] == 'line':
      s = self.line(X, Y, a['size'], a['facing'])
    elif a['shape'] == 'square':
      s = self.square(X, Y, a['size'])
    elif a['shape'] == 'triangl':
      s = self.triangle(a['facing'], p)
    elif a['shape'] == 'diamond':
      s = self.diamond(a['facing'], p)
    else:
      s = self.set_text(a['shape'], X, Y)
    return s

  def circle(self, size, stroke_width, p):
    if size == 'large': 
      size = self.sizeUu / 2
      sum_two_sides = (size**2 + size**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - stroke_width
    elif size == 'medium':
      r = (self.sizeUu / 2 - stroke_width) # normal size
    elif size == 'small':
      r = (self.sizeUu / 3 - stroke_width) 
    else:
      raise ValueError(f"Cannot set circle to {size} size")
    circle = Circle(cx=str(p.mid[0]), cy=str(p.mid[1]), r=str(r))
    return circle

  def line(self, X, Y, size, facing):
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    facing = 'north' if facing == 'south' else facing
    facing = 'east' if facing == 'west' else facing
    if size == 'large' and facing == 'north':
      x      = str(X + self.sizeUu / 3 + self.hw)
      y      = str(Y - self.sizeUu / 3 + self.hw)
      width  = str(self.sizeUu / 3 - self.fw)
      height = str((self.sizeUu / 3 * 2 + self.sizeUu) - self.fw)
    elif size == 'large' and facing == 'east':
      x      = str(X - self.sizeUu / 3 + self.hw)
      y      = str(Y + self.sizeUu / 3 + self.hw)
      width  = str((self.sizeUu / 3 * 2 + self.sizeUu) - self.fw)
      height = str(self.sizeUu / 3 - self.fw)
    elif size == 'medium' and facing == 'north':
      x      = str(X + self.sizeUu / 3 + self.hw)
      y      = str(Y + self.hw)
      width  = str(self.sizeUu / 3 - self.fw)
      height = str(self.sizeUu - self.fw)
    elif size == 'medium' and facing == 'east':
      x      = str(X + self.hw)
      y      = str(Y + self.sizeUu / 3 + self.hw)
      width  = str(self.sizeUu - self.fw)
      height = str(self.sizeUu / 3 - self.fw)
    elif size == 'small' and facing == 'north':
      x      = str(X + self.sizeUu / 3 + self.hw)
      y      = str(Y + self.sizeUu / 4 + self.hw)
      width  = str(self.sizeUu / 3 - self.fw)
      height = str(self.sizeUu / 2 - self.fw)
    elif size == 'small' and facing == 'east':
      x      = str(X + self.sizeUu / 4 + self.hw)
      y      = str(Y + self.sizeUu / 3 + self.hw)
      width  = str(self.sizeUu / 2 - self.fw)
      height = str(self.sizeUu / 3 - self.fw)
    else:
      raise ValueError(f"Cannot set line to {size}")
    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def square(self, X, Y, size):
    if size == 'medium':
      x      = str(X + self.hw)
      y      = str(Y + self.hw)
      width  = str(self.sizeUu - self.fw)
      height = str(self.sizeUu - self.fw)
    elif size == 'large':
      third  = self.sizeUu / 3
      x      = str(X - third / 2 + self.hw)
      y      = str(Y - third / 2 + self.hw)
      width  = str(self.sizeUu + third - self.fw)
      height = str(self.sizeUu + third - self.fw)
    elif size == 'small':
      third  = self.sizeUu / 3
      x      = str(X + self.fw + third)
      y      = str(Y + self.fw + third)
      width  = str(third - self.fw)
      height = str(third - self.fw)
    else:
      raise ValueError(f"Cannot make square with {size}")
    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def triangle(self, facing, p):
    if facing == 'west': 
      points = p.w + p.ne + p.se + p.w
    elif facing == 'east': 
      points = p.nw + p.e + p.sw + p.nw
    elif facing == 'north': 
      points = p.sw + p.n + p.se + p.sw
    elif facing == 'south':
      points = p.nw + p.ne + p.s + p.nw
    else:
      raise ValueError("Cannot face triangle {}".format(facing))
    polyg = Polygon(points=",".join(map(str, points)))
    return polyg

  def diamond(self, facing, p):
    if facing == 'all': 
      points = p.w + p.n + p.e + p.s + p.w
    elif facing == 'west': 
      points = p.w + p.n + p.s + p.w
    elif facing == 'east': 
      points = p.n + p.e + p.s + p.n
    elif facing == 'north': 
      points = p.w + p.n + p.e + p.w
    elif facing == 'south':
      points = p.w + p.e + p.s + p.w
    else:
      raise ValueError(f"Cannot face diamond {facing}")
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

    self.width   = 1080  # px
    self.height  = 1080
    self.size    = (54 / self.factor)  
    self.maxCols = int(20 * self.factor)
    self.maxRows = int(20 * self.factor)  # num of row  
    '''
    self.width   = 1122.5197  # px
    self.height  = 793.70081
    self.size    = (48 / self.factor)  
    self.maxCols = int(22 * self.factor)
    self.maxRows = int(15 * self.factor)  # num of row  
    '''
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
    self.cells = self.c.transform(self.control, cells)

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
    positions = self.b.read() 
    #blocksize = m.get(model=self.model)[2]
    blocksize = m.read(model=self.model)[2]
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
    top = list()
    for paintOrder in range(2): # background first then foreground
      for y in range(self.maxRows):
        print('.', end='', flush=True)
        for x in range(self.maxCols):
          pos = tuple([x, y])
          (xSizeMm, ySizeMm) = self.blocknum_to_uu(pos)
          cell = self.get_cell_by_position(pos)
          data = self.cells[cell]
          if not data:
            continue # checker-board background !
          gid = f"{cell}{paintOrder}"
          sid = f"{cell}{paintOrder}-{x}-{y}"
          if paintOrder:
            #print(f'{gid} ', end='', flush=True)
            shape = self.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method here
            group[gid].add(shape) 
          else:
            #print(f'{gid} ', end='', flush=True)
            shape = self.backgrounds(cell, xSizeMm, ySizeMm)
            shape.set_id(sid)    # calling an inkex method
            group[gid].add(shape)
        #print("")
    return None

  def build(self, svg, top_order):
    ''' Generate inkex groups for the svg renderer to use  
    '''
    #print(top_order) Large cells should be last
    group = {}  # hold a local reference to groups created in svg doc
    stroke_width = {}
    sw0 = svg.unittouu(0) # hide the cracks between the background tiles
    for g in top_order:
      # draw background  cells
      bg = Group()
      bg.set_id(f'{g}0')
      bg.style = { 'fill' : self.cells[g]['bg'], 'stroke-width': sw0, 'stroke':'#FFF' }
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

  '''
  #def triangle(self, cell, X, Y, a):
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
      #points = [ x[0], y[1], x[2], y[0], x[2], y[2], x[0], y[1] ]
      #points = [ x[1], y[0], x[3], y[1], x[1], y[2], x[1], y[0] ]
      #points = [ x[0], y[2], x[4], y[0], x[3], y[2], x[0], y[2] ]
      #points = [ x[1], y[5], x[4], y[2], x[2], y[5], x[1], y[5] ]
        south
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
    all   points = [ x[0], y[1], x[4], y[0], x[3], y[1], x[4], y[2], x[0], y[1] ]
    west  points = [ x[0], y[1], x[6], y[0], x[6], y[2], x[0], y[1] ]
    east  points = [ x[5], y[0], x[3], y[1], x[5], y[2], x[5], y[0] ]
    north points = [ x[0], y[4], x[4], y[0], x[3], y[4], x[0], y[4] ]
    south points = [ x[0], y[3], x[4], y[2], x[2], y[3], x[0], y[3] ]

    points = p.nw + p.e + p.sw + p.nw
    #points = [ x[1], y[0], x[3], y[1], x[1], y[2], x[1], y[0] ]
    hw = stroke_width / 2  # stroke width is halved to avoid overspill
    fw = stroke_width      # full width
    x = [ 
    0 X + self.fw,
    1 X + self.hw,
    2 X + self.sizeUu - self.hw,
    3 X + self.sizeUu - self.fw, 
    4 X + self.sizeUu / 2,
    5 X + self.sizeUu / 2 + self.hw,
    6 X + self.sizeUu / 2 - self.hw,
    ]
    y = [
    0 Y + self.fw, 
    1 Y + self.sizeUu / 2, 
    2 Y + self.sizeUu - self.fw,
    3 Y + self.sizeUu / 2 + self.hw, 
    4 Y + self.sizeUu / 2 - self.hw
    ]
  '''

