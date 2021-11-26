#!/usr/bin/env python3
# coding=utf-8
import inkex
from draw import Draw
from configure import Layout

class Cells():

  def __init__(self, options):
    ''' rebuild selected cells according to user input 
    '''
    self.requested = {
      'shape': options.shape,
      'shape_size': options.size,
      'shape_facing': options.facing,
      'top': options.top,
      'stroke_width': int(options.width)
    }
    self.bg = options.bg
    layout = Layout()  #  TODO how to remember factor=float(self.options.scale)) from input ??? 
    self.draw = Draw([layout.size, layout.width, layout.height])
    self.layout = layout

  def update(self, svg, layer):
    ''' all the elems according to cell id
        for example f1-0-0 .. f1-360-360 '''
    message = None
    shapes = svg.selection.first() # assume that first in ElementList is <g />
    thisId = shapes.get('id')

    if self.requested['shape'] == 'triangle' and self.requested['shape_size'] == 'large':
      message = 'Large triangles are not possible, ignoring this request.'
    elif shapes is not None:
      # update the background style, but only if we're given a new value
      self.set_background(thisId, self.bg, svg) 
      self.set_foreground(shapes, self.requested)
      shapes.style['stroke-width'] = svg.unittouu(self.requested['stroke_width'])
      # add the top elems last
      if self.requested['top']:
        group = svg.getElementById(thisId)
        groupLast = group
        svg.remove(group)
        svg.add(groupLast)
    else:
      message = f"group id={thisId} not found"
    return message

  def set_background(self, thisId, givenFill, svg):
    ''' force the selection to a background cell
        because clickers can hit either
    '''
    cell = thisId[0]
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
        (x, y) = self.layout.blocknum_to_uu(int(xBlocknum), int(yBlocknum))
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
    self.version = 'v1'
    if self.svg.selection:
      c = Cells(self.options)
      message = c.update(self.svg)
      if message:
        self.msg(message)
    else:
      self.msg("After opening up a model you have to select a cell for editing")

if __name__ == '__main__':
  Recurrink().run()
