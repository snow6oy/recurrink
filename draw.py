#!/usr/bin/env python3
# coding=utf-8

import inkex
from inkex import Group, Circle, Rectangle, Polygon, TextElement

import pprint, math

class Draw:
  '''
  use viewer to do the maths to render a cell
  '''
  def __init__(self, baseUnit):
    ''' units must be in sync with Layout.sizeUu '''
    self.sizeUu  = baseUnit[0] # size
    self.x_offset = baseUnit[1] # x offset
    self.y_offset = baseUnit[2] # y offset

  def backgrounds(self, cell, x, y):
    '''
    the first cell painted onto the grid is a filled rectangle
    see Builder for a list of the available colours
    '''
    w = str(self.sizeUu)
    h = str(self.sizeUu)
    bg = Rectangle(x=str(x), y=str(y), width=w, height=h)
    return bg

  def shape(self, cell, X, Y, a):
    '''
    create a shape from a cell for adding to a group
    '''
    if a['shape'] == 'circle':
      s = self.set_circle(cell, X, Y, a)
    elif a['shape'] == 'line':
      s = self.set_line(cell, X, Y, a)
    elif a['shape'] == 'square':
      s = self.set_square(cell, X, Y, a)
    elif a['shape'] == 'triangle':
      s = self.set_triangle(cell, X, Y, a)
    else:
      s = self.set_text(a['shape'], X, Y)

    return s

  def set_circle(self, cell, X, Y, a):
    halfw = a['stroke_width'] / 2
    fullw = a['stroke_width']

    if a['shape_size'] == 'large': 
      size = self.sizeUu / 2
      # pythagoras was a pythonista :)
      sum_two_sides = (size**2 + size**2)
      r = math.sqrt(sum_two_sides) - halfw
    elif a['shape_size'] == 'medium':
      r = (self.sizeUu / 2 - halfw) # normal size
    else:
      raise ValueError(f"Cannot set circle <{cell}> to {a['shape_size']} size")

    x = str(X + self.sizeUu / 2)
    y = str(Y + self.sizeUu / 2)
    circle = Circle(cx=x, cy=y, r=str(r))
    #circle.label = cell
    return circle

  def set_line(self, cell, X, Y, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
    '''
    lines can be orientated along a north-south axis or east-west axis
    but the user can choose any of the four cardinal directions
    here we silently collapse the non-sensical directions
    '''
    a['shape_facing'] = 'north' if a['shape_facing'] == 'south' else a['shape_facing']
    a['shape_facing'] = 'east' if a['shape_facing'] == 'west' else a['shape_facing']

    if a['shape_size'] == 'large' and a['shape_facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y - self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
    elif a['shape_size'] == 'large' and a['shape_facing'] == 'east':
      x      = str(X - self.sizeUu / 3 + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
      height = str(self.sizeUu / 3 - fullw)
    elif a['shape_size'] == 'medium' and a['shape_facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str(self.sizeUu - fullw)
    elif a['shape_size'] == 'medium' and a['shape_facing'] == 'east':
      x      = str(X + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu / 3 - fullw)
    else:
      raise ValueError(f"Cannot set {cell} to {a['shape_size']}")

    rect = Rectangle(x=x, y=y, width=width, height=height)
    #rect.label = cell
    return rect

  def set_square(self, cell, xSizeMm, ySizeMm, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
      
    if a['shape_size'] == 'medium':
      x      = str(xSizeMm + halfw)
      y      = str(ySizeMm + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu - fullw)
    elif a['shape_size'] == 'large':
      third  = self.sizeUu / 3
      x      = str(xSizeMm - third / 2 + halfw)
      y      = str(ySizeMm - third / 2 + halfw)
      width  = str(self.sizeUu + third - fullw)
      height = str(self.sizeUu + third - fullw)
    else:
      raise ValueError("Cannot set rectangle {}".format(cell))

    rect = Rectangle(x=x, y=y, width=width, height=height)
    #rect.label = cell
    return rect

  def set_triangle(self, cell, X, Y, a):

    fullw = a['stroke_width']
    # stroke width is halved for repositioning
    halfw = a['stroke_width'] / 2
    #X = int(x)   integers for addition. points[] is made a string collection last
    #Y = int(y)

    #raise ValueError(f"X {type(X)} fw {type(fullw)} mm {type(self.sizeUu)}")
    if a['shape_facing'] == 'west': 
      points = [
        X + fullw, Y + self.sizeUu / 2, 
        X + self.sizeUu - halfw, Y + fullw, 
        X + self.sizeUu - halfw, Y + self.sizeUu - fullw,
        X + fullw, Y + self.sizeUu / 2
      ]
    elif a['shape_facing'] == 'east': 
      points = [
        X + halfw, Y + fullw, 
        X + self.sizeUu - fullw, Y + self.sizeUu / 2,
        X + halfw, Y + self.sizeUu - fullw,
        X + halfw, Y + fullw
      ]
    elif a['shape_facing'] == 'north': 
      points = [
        X + fullw, Y + self.sizeUu - halfw,
        X + self.sizeUu / 2, Y + fullw,
        X + self.sizeUu - fullw, Y + self.sizeUu - halfw,
        X + fullw, Y + self.sizeUu - halfw
      ]
    elif a['shape_facing'] == 'south':
      points = [
        X + halfw, Y + halfw, 
        X + self.sizeUu / 2, Y + self.sizeUu - fullw, 
        X + self.sizeUu - halfw, Y + halfw,
        X + halfw, Y + halfw
      ]
    else:
      raise ValueError("Cannot face triangle {}".format(a['shape_facing']))
    
    polyg = Polygon(points=",".join(map(str, points)))
    #polyg.label = cell
    return polyg
  
  def set_text(self, shape, X, Y):
    '''
    when the shape is unknown print as text in the cell
    '''
    x = str(X + 3)
    y = str(Y + 40)
    textElement = TextElement(x=x, y=y)
    textElement.text = shape
    # self.debug(textElement)
    return textElement

  """
  def set_foreground(self, shapes, requested):
    ''' replace shape based on user input '''
    for elem in shapes:
      idItems = elem.get_id().split('-')
      if len(idItems) == 3:
        (gid, x, y) = idItems 
        # calculate mm sizes based on blocknums
        ySizeMm = self.y_offset + (int(y) * self.sizeUu)
        xSizeMm = self.x_offset + (int(x) * self.sizeUu)
      else:
        raise ValueError(f"Unexpected format id={idItems}")
      newShape = self.shape(gid[0], xSizeMm, ySizeMm, requested)
      elem.replace_with(newShape)
      # set id after replacement to avoid collisions
      elem.set_id(f"{gid}-{x}-{y}")

    return None

  def sort_groups(self, searchId, svg, layer):
    ''' remove the top elems and then add them at the bottom '''
    msg = None
    topGroup = None
    groups = self.get_fg_groups(svg)
    if not groups:
      raise ValueError(f"search id {searchId} not matching")
    addList = [] # handy for debug
    for g in groups:
      addList.append(g.get_id()) # remember the name and position before zapping
      if searchId[0] == g.get_id()[0]:  # user can click either c1 or c0
        topGroup = g
        addList.append('+') # mark with a + to remember the name and position before zapping
        g.delete()
    if topGroup is not None:
      layer.add(topGroup)
    else:
      raise ValueError(f"search id {searchId} not matching" + "\n".join(addList))
    return None

  # TODO read the docs and try to simplify
  # https://inkscape-extensions-guide.readthedocs.io/en/latest/inkex-modules.html#inkex.svg.SvgDocumentElement.getElementById
  def get_elems_by_id(self, svg, searchId):
    ''' all the elems according to cell
        for example fg-a-0-0 .. fg-a-360-360 '''
    elem = None 
    style = None
    ns = {"": 'http://www.w3.org/2000/svg'}
    for g in svg.find('g', ns):
      if g.attrib['id'] == searchId:  # e.g. fg-a
        elem = g
        if 'style' in g.attrib:
          style = g.attrib['style']
        break
    return (elem, style)

  def get_fg_groups(self, svg):
    ''' get a list of top-level groups
        for example fg-a .. fg-x
    '''
    groups = []
    ns = {"": 'http://www.w3.org/2000/svg'}
    for g in svg.find('g', ns):
      paintOrder = int(g.attrib['id'][1])  # id = c1
      if paintOrder == 1:    # background has paintOrder 0
        groups.append(g)
    return groups

  def set_background(self, searchId, givenFill, svg):
    # TODO check that #FFF #ffffff etc are consistent
    #cell = searchId.split('-')[1]
    cell = searchId[0]
    #bgId = f"bg-{cell}"
    bgId = f"{cell}0"
    (shape, style) = self.get_elems_by_id(svg, bgId)
    thisFill = style.split(':')[1]
    if thisFill != givenFill:  # background needs to change
      shape.set('style', f"fill:{givenFill}")
    return shape
  """
