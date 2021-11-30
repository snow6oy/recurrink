#!/usr/bin/env python3
# coding=utf-8
import inkex
from draw import Draw
from configure import Layout

class Cells(Layout):
  ''' replace cells according to user input
  '''
  def __init__(self, options, factor=None):
    self.requested = {
      'shape': options.shape,
      'shape_size': options.size,
      'shape_facing': options.facing,
      'top': options.top,
      'stroke_width': int(options.width)
    }
    self.bg = options.bg 
    super().__init__(factor=float(factor))
    self.draw = Draw([self.size, self.width, self.height])

  def update(self, svg):
    ''' all the elems according to cell id
        for example f1-0-0 .. f1-360-360 '''
    message = None
    shapes = svg.selection.first() # assume that first in ElementList is <g />

    if self.requested['shape'] == 'triangle' and self.requested['shape_size'] == 'large':
      message = 'Large triangles are not possible, ignoring this request.'
    elif shapes is not None:
      # update the background style, but only if we're given a new value
      self.set_background(shapes, self.bg, svg) 
      self.set_foreground(shapes, self.requested)
      shapes.style['stroke-width'] = svg.unittouu(self.requested['stroke_width'])
      # add the top elems last
      if self.requested['top']:
        group = svg.getElementById(thisId)
        groupLast = group
        svg.remove(group)
        svg.add(groupLast)
    else:
      message = "not found"
    return message

  def set_background(self, shapes, givenFill, svg):
    ''' force the selection to a background cell
        because clickers can hit either
    '''
    cell = shapes.get('id')[0]
    bgElem = svg.getElementById(f"{cell}0")
    # TODO check that #FFF #ffffff etc are consistent
    if bgElem.style['fill'] != givenFill:  # background needs to change
      bgElem.set('style', f"fill:{givenFill}")

  def set_foreground(self, shapes, requested):
    ''' replace shape based on user input '''
    message = ""
    for elem in shapes:
      idItems = elem.get_id().split('-')
      if len(idItems) == 3:
        (gid, xBlocknum, yBlocknum) = idItems 
        # calculate coordinates based on blocknums
        (x, y) = self.blocknum_to_uu(int(xBlocknum), int(yBlocknum))
      else:
        raise ValueError(f"Unexpected format id={idItems}")
      message += f"id {gid[0]} {x} {y}\n"
      newShape = self.draw.shape(gid[0], float(x), float(y), requested)
      elem.replace_with(newShape)
      # set id after replacement to avoid collisions
      elem.set_id(f"{gid}-{x}-{y}")
    #return message
    return None

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
    rinkId = self.svg.get('recurrink-id')
    factor = self.svg.get('recurrink-factor')
    if not rinkId:
      inkex.errormsg("This extension only knows about SVGs created from a .rink file")
    elif self.svg.selection:
      # c = Cells(self.options, factor)
      c = Cells(self.options, factor)
      message = c.update(self.svg)
      if message:
        inkex.errormsg(message)
    else:
      inkex.errormsg("After opening up a model you have to select a cell for editing")

if __name__ == '__main__':
  Recurrink().run()
