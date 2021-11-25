#!/usr/bin/env python3
# coding=utf-8
import inkex
from inkex import Circle, Group
from draw import Draw
from configure import Layout

#from inkex import Group, Circle, Rectangle, Polygon, TextElement
#import pprint, math

class EditCells():

  def __init__(self, options, baseUnit):

    self.requested = {
      'shape': options.shape,
      'shape_size': options.size,
      'shape_facing': options.facing,
      'top': options.top,
      'stroke_width': int(options.width)
    }
    self.bg = options.bg
    ''' units must be in sync with Layout.sizeUu '''
    self.sizeUu  = baseUnit[0] # size
    self.x_offset = baseUnit[1] # x offset
    self.y_offset = baseUnit[2] # y offset
    self.draw = Draw(baseUnit)

  def update(self, svg, layer):
    ''' all the elems according to cell
        for example fg-a-0-0 .. fg-a-360-360 '''
    message = None
    shapes = svg.selection.first() # assume that first in ElementList is <g />
    searchId = shapes.get('id')
    #shapes = svg.getElementById(searchId)
    #shapes = self.get_elems_by_id(svg, searchId)[0]

    if self.requested['shape'] == 'triangle' and self.requested['shape_size'] == 'large':
      message = 'Large triangles are not possible, ignoring this request.'
    elif shapes is not None:
      # update the background style, but only if we're given a new value
      self.set_background(searchId, self.bg, svg) 
      a = self.set_foreground(shapes, self.requested)
      raise Warning(a)
      #elem.style['stroke-width'] = svg.unittouu(self.requested['stroke_width'])
      shapes.style['stroke-width'] = svg.unittouu(self.requested['stroke_width'])
      # add the top elems last
      if self.requested['top']:
        self.sort_groups(searchId, svg, layer) # TODO why two SVGs
    else:
      message = f"group id={searchId} not found"
    return message

  def set_foreground(self, shapes, requested):
    ''' replace shape based on user input '''
    a = ""
    for elem in shapes:
      idItems = elem.get_id().split('-')
      x = elem.attrib['x']  # id = c1
      y = elem.attrib['y']  # id = c1
      if len(idItems) == 3:
        (gid, _, _) = idItems 
        # calculate mm sizes based on blocknums
        #ySizeMm = self.y_offset + (int(y) * self.sizeUu)
        #xSizeMm = self.x_offset + (int(x) * self.sizeUu)
      else:
        raise ValueError(f"Unexpected format id={idItems}")
      a += f"id {gid[0]} {x} {y}\n"
      newShape = Circle(cx=x, cy=y, r="24")
      #newShape = self.draw.shape(gid[0], float(x), float(y), requested)
      elem.replace_with(newShape)
      # set id after replacement to avoid collisions
      elem.set_id(f"{gid}-{x}-{y}")
    return a

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
  '''
  def get_elems_by_id(self, svg, searchId):
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
  '''

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
    ''' force the selection to a background cell
        because clickers can hit either
    '''
    cell = searchId[0]
    bgId = f"{cell}0"
    bgElem = svg.getElementById(bgId)
    # TODO check that #FFF #ffffff etc are consistent
    if bgElem.style['fill'] != givenFill:  # background needs to change
      bgElem.set('style', f"fill:{givenFill}")

class Recurrink(inkex.EffectExtension):
  ''' draw recurring patterns using inkscape '''
  def add_arguments(self, pars):
    pars.add_argument("--tab",    type=str, dest="tab")
    pars.add_argument("--shape",  default='square', help="Replace one shape with another")
    pars.add_argument("--size",   default='normal', help="Increase shape size (not triangles)")
    pars.add_argument("--facing", default='north', help="Rotate shapes (not squares or circles)")
    pars.add_argument("--width",  default=0, help="Border thickness as a number 0-9")
    pars.add_argument("--bg",     default='#FFFFFF', help="Change the background colour")
    pars.add_argument("--top",    default=False, type=inkex.Boolean, help="Stay on top when overlapping")

  def effect(self):  # effect because generate is a subset
    ''' check if svg is a recurrence and then apply inputs
    '''
    self.version = 'v1'
    layer = self.svg.get_current_layer()
    # adjust base units according to input
    layout = Layout()  #  TODO how to remember factor=float(self.options.scale)) from input ??? 

    if self.svg.selection: #  and self.is_recurrence():
      # elem = self.svg.selection.first() # assume that first in ElementList is <g />
      # message = elem.get('id')
      # for e in elem:
      #  message += e.get('id')
      #shapes = svg.getElementById(searchId)
      e = EditCells(self.options, [layout.size, layout.width, layout.height])
      message = e.update(self.svg, layer)
      if message:
        self.msg(message)
    else:
      self.msg("After opening up a model you have to select a cell for editing")

if __name__ == '__main__':
  Recurrink().run()

