#!/usr/bin/env python3
# coding=utf-8

#import os
#import sys
#import csv
#import json
#import glob
#import hmac
#import random
#import getopt

import math
import inkex
from inkex import Group, Circle, Rectangle, Polygon, TextElement

class Draw:
  ''' does the maths to render a cell
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
    if a['shape'] == 'circle':
      s = self.set_circle(cell, X, Y, a)
    elif a['shape'] == 'line':
      s = self.set_line(cell, X, Y, a)
    elif a['shape'] == 'square':
      s = self.set_square(cell, X, Y, a)
    elif a['shape'] == 'triangle':
      s = self.set_triangle(cell, X, Y, a)
    elif a['shape'] == 'diamond':
      s = self.set_diamond(cell, X, Y, a)
    else:
      s = self.set_text(a['shape'], X, Y)

    return s

  def set_circle(self, cell, X, Y, a):
    halfw = a['stroke_width'] / 2
    fullw = a['stroke_width']

    if a['size'] == 'large': 
      size = self.sizeUu / 2
      sum_two_sides = (size**2 + size**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - halfw
    elif a['size'] == 'medium':
      r = (self.sizeUu / 2 - halfw) # normal size
    else:
      raise ValueError(f"Cannot set circle <{cell}> to {a['size']} size")

    x = str(X + self.sizeUu / 2)
    y = str(Y + self.sizeUu / 2)
    circle = Circle(cx=x, cy=y, r=str(r))
    #circle.label = cell
    return circle

  def set_line(self, cell, X, Y, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    a['facing'] = 'north' if a['facing'] == 'south' else a['facing']
    a['facing'] = 'east' if a['facing'] == 'west' else a['facing']

    if a['size'] == 'large' and a['facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y - self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
    elif a['size'] == 'large' and a['facing'] == 'east':
      x      = str(X - self.sizeUu / 3 + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
      height = str(self.sizeUu / 3 - fullw)
    elif a['size'] == 'medium' and a['facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str(self.sizeUu - fullw)
    elif a['size'] == 'medium' and a['facing'] == 'east':
      x      = str(X + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu / 3 - fullw)
    else:
      raise ValueError(f"Cannot set {cell} to {a['size']}")

    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def set_square(self, cell, xSizeMm, ySizeMm, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
      
    if a['size'] == 'medium':
      x      = str(xSizeMm + halfw)
      y      = str(ySizeMm + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu - fullw)
    elif a['size'] == 'large':
      third  = self.sizeUu / 3
      x      = str(xSizeMm - third / 2 + halfw)
      y      = str(ySizeMm - third / 2 + halfw)
      width  = str(self.sizeUu + third - fullw)
      height = str(self.sizeUu + third - fullw)
    else:
      raise ValueError("Cannot set rectangle {}".format(cell))

    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def set_triangle(self, cell, X, Y, a):

    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2 # stroke width is halved for repositioning

    if a['facing'] == 'west': 
      points = [
        X + fullw, Y + self.sizeUu / 2, 
        X + self.sizeUu - halfw, Y + fullw, 
        X + self.sizeUu - halfw, Y + self.sizeUu - fullw,
        X + fullw, Y + self.sizeUu / 2
      ]
    elif a['facing'] == 'east': 
      points = [
        X + halfw, Y + fullw, 
        X + self.sizeUu - fullw, Y + self.sizeUu / 2,
        X + halfw, Y + self.sizeUu - fullw,
        X + halfw, Y + fullw
      ]
    elif a['facing'] == 'north': 
      points = [
        X + fullw, Y + self.sizeUu - halfw,
        X + self.sizeUu / 2, Y + fullw,
        X + self.sizeUu - fullw, Y + self.sizeUu - halfw,
        X + fullw, Y + self.sizeUu - halfw
      ]
    elif a['facing'] == 'south':
      points = [
        X + halfw, Y + halfw, 
        X + self.sizeUu / 2, Y + self.sizeUu - fullw, 
        X + self.sizeUu - halfw, Y + halfw,
        X + halfw, Y + halfw
      ]
    else:
      raise ValueError("Cannot face triangle {}".format(a['facing']))
    
    polyg = Polygon(points=",".join(map(str, points)))
    #polyg.label = cell
    return polyg
  
  def set_diamond(self, cell, X, Y, a):

    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2 # stroke width is halved for repositioning

    x = [ 
      X + fullw,
      X + halfw,
      X + self.sizeUu - halfw,
      X + self.sizeUu - fullw, 
      X + self.sizeUu / 2,
      X + self.sizeUu / 2 + halfw,
      X + self.sizeUu / 2 - halfw,
    ]
    y = [
      Y + fullw, 
      Y + self.sizeUu / 2, 
      Y + self.sizeUu - fullw,
      Y + self.sizeUu / 2 + halfw, 
      Y + self.sizeUu / 2 - halfw
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
  def __init__(self, factor=1.0):
    ''' 
    original calculation was page size 210 x 297 mm (A4 portrait)
    since unit are not millimeters this table is inaccurate

    factor    size   col  row   x os   y os
      0.5     24.0     7   11   21.0   16.5  twice as big
      1.0     12.0    15   22   15.0   16.5  do nothing
      2.0      6.0    30   44   15.0   16.5  half size
    '''
    self.width   = 1122.5197  # px
    self.height  = 793.70081
    self.size    = (48 / factor)  
    self.maxCols = int(22 * factor)
    self.maxRows = int(15 * factor)  # num of row  
    numOfMargins = 2
    self.xOffset = (self.width  - (self.maxCols * self.size)) / numOfMargins # 33.25985000000003
    self.yOffset = (self.height - (self.maxRows * self.size)) / numOfMargins # 36.85040500000002
    super().__init__([self.size, self.xOffset, self.yOffset])

  ''' load database of named model or use given db
  def add(self, model, db=None):
    if db is None:
      json_file = f"/tmp/{model}.rink"
      with open(json_file) as f:
        db = json.load(f)
      self.get = db
    elif db:
      self.get = db
    else: 
      raise ValueError(f"cannot find model {model}. db len is {len(db)}")
    return self.get
  '''
  def add(self, view_data):
    ''' load database of named model or use given db'''
    if view_data:
      self.get = view_data
    else: 
      raise ValueError(f"cannot find cells for {view_data}.")
    return self.get

  def get_cell(self, cell):
    if cell in self.get['cells']:
      return self.get['cells'][cell]
    else:
      raise KeyError(f"unknown cell {cell}")

  def uniq_cells(self):
    ''' provide a unique list of cells using in the model 
    '''  
    return list(self.get['cells'].keys())

  def blocksize(self):
    '''
    send the model co-ordinate range as a tuple
    '''
    blocksize = self.get['size']
    return tuple(blocksize)

  '''
  def get_id(self):
    was supposed to lookup a digest such as 3e8539a9929c0b2595f44146f1b3770c
    return self.get['id']
  '''

  def get_cell_by_position(self, x, y):
    '''
    repeat the block to fit the canvas
    1. calculate the block number using integer division, blocksize and counter
    2. then new counter = counter - blocknumber * blocksize
    '''
    cell = None
    (x_blocksize, y_blocksize) = self.blocksize()

    y_blocknum = int(y / y_blocksize)
    Y = y - (y_blocknum * y_blocksize)

    x_blocknum = int(x / x_blocksize)
    X = x - (x_blocknum * x_blocksize)
    #print(f'xy({x}, {y})  XY({X}, {Y})  blocknum({x_blocknum}, {y_blocknum})')
    current_posn = (X, Y) # tuples are immutable

    for c in self.get['cells']:
      for p in self.get['cells'][c]['positions']:
        posn = tuple(p)
        if posn == current_posn:
          cell = c
          break
    return cell

  def blocknum_to_uu(self, xBlocknum, yBlocknum):
    ''' convert a position in the grid to pixels 
    '''
    xUu = self.xOffset + (xBlocknum * self.size)
    yUu = self.yOffset + (yBlocknum * self.size)
    return xUu, yUu

  #def render(self, draw, group, strokeWidth):
  def render(self, group, strokeWidth):
    ''' draw out a model by repeating blocks across the canvas
    '''
    # TODO the algorithm should follow JSON 
    for paintOrder in range(2):
      for y in range(self.maxRows):
        for x in range(self.maxCols):
          (xSizeMm, ySizeMm) = self.blocknum_to_uu(x, y)
          cell = self.get_cell_by_position(x, y)
          data = self.get_cell(cell)
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
