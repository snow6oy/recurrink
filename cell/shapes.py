import math
'''
import pprint
import xml.etree.ElementTree as ET
from shapes import Geomink # Rectangle #, Flatten
from flatten import Flatten
from shapely import box
pp = pprint.PrettyPrinter(indent = 2)
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

class Shapes:
  def __init__(self, scale, cellsize):
    self.scale    = scale
    self.cellsize = cellsize

  def foreground(self, x, y, cell):
    ''' create a shape from a cell for adding to a group
  
        fix for update --mm is to ignore stroke whenever it causes width to be less than one
    '''
    facing = cell['facing']
    shape = cell['shape']
    size = cell['size']
    hsw = (cell['stroke_width'] / 2) * self.scale
    sw = cell['stroke_width'] * self.scale
    p = Points(x, y, sw, self.cellsize)
    #print(f"{self.cellsize=} {size=} {shape=} {x=} {y=} half stroke width:{hsw=} stroke width:{sw=}")
    if shape == 'circle':
      s = self.circle(size, sw, p)
    elif shape == 'square':
      s = self.square(x, y, size, hsw, sw)
      if s['width'] < 1 or s['height'] < 1:
        s = self.square(x, y, size, hsw, 0)
    elif shape == 'line':
      s = self.line(x, y, facing, size, hsw, sw)
      if s['width'] < 1 or s['height'] < 1:
        s = self.line(x, y, facing, size, hsw, 0)
    elif shape == 'triangl':
      s = self.triangle(facing, p)
    elif shape == 'diamond':
      s = self.diamond(facing, p)
    else:
      print(f"Warning: do not know {shape}")
      s = self.text(shape, x, y)

    ''' Value Errors are redundant since errors are trapped above
    if 'width' in s and s['width'] < 1:
      raise ValueError(f"square too small width: {s['width']} orig {cell['width']}")
    elif 'height' in s and s['height'] < 1:
      raise ValueError(f"square too small height: {s['height']}")
    '''
    s['name'] = shape
    return s

  def circle(self, size, stroke_width, p):
    cs = self.cellsize
    if size == 'large': 
      cs /= 2
      sum_two_sides = (cs**2 + cs**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - stroke_width
    elif size == 'medium':
      r = (cs / 2 - stroke_width) # normal cs
    elif size == 'small':
      r = (cs / 3 - stroke_width) 
    else:
      raise ValueError(f"Cannot set circle to {size} size")
    return { 'cx': p.mid[0], 'cy': p.mid[1], 'r': r }

  def square(self, x, y, size, hsw, sw):
    cs = self.cellsize
    if size == 'medium':
      x      = (x + hsw)
      y      = (y + hsw)
      width  = (cs - sw)
      height = (cs - sw)
    elif size == 'large':
      third  = cs / 3
      x      = (x - third / 2 + hsw)
      y      = (y - third / 2 + hsw)
      width  = (cs + third - sw)
      height = (cs + third - sw)
    elif size == 'small':
      third  = cs / 3
      x      = (x + third + hsw)
      y      = (y + third + hsw)
      width  = (third - sw)
      height = (third - sw)
    else:
      raise ValueError(f"Cannot make square with {size}")
    return { 'x': x, 'y': y, 'width': width, 'height': height }

  def line(self, x, y, facing, size, hsw, sw):
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    cs = self.cellsize
    facing = 'north' if facing == 'south' else facing
    facing = 'east' if facing == 'west' else facing
    if size == 'large' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y - cs / 3 + hsw)
      width  = (cs / 3 - sw)
      height = ((cs / 3 * 2 + cs) - sw)
    elif size == 'large' and facing == 'east':
      x      = (x - cs / 3 + hsw)
      y      = (y + cs / 3 + hsw)
      width  = ((cs / 3 * 2 + cs) - sw)
      height = (cs / 3 - sw)
    elif size == 'medium' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y + hsw)
      width  = cs / 3 - sw
      height = (cs - sw)
    elif size == 'medium' and facing == 'east':
      x      = (x + hsw)
      y      = (y + cs / 3 + hsw)
      width  = (cs - sw)
      height = (cs / 3 - sw)
    elif size == 'small' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y + cs / 4 + hsw)
      width  = (cs / 3 - sw)
      height = (cs / 2 - sw)
    elif size == 'small' and facing == 'east':
      x      = (x + cs / 4 + hsw)
      y      = (y + cs / 3 + hsw)
      width  = (cs / 2 - sw)
      height = (cs / 3 - sw)
    else:
      raise ValueError(f"Cannot set line to {size} {facing}")
    return { 'x': x, 'y': y, 'width': width, 'height': height }

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
      raise ValueError(f"Cannot face triangle {facing}")
    return { 'points': ','.join(map(str, points)) }

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
    return { 'points': ','.join(map(str, points)) }

  def text(self, name, x, y):
    return { 'x': x, 'y': y }
'''
the
end
'''
