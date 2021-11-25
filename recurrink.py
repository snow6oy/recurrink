#!/usr/bin/env python3
# coding=utf-8
import inkex
from inkex import Circle, Group
from draw import Draw
from configure import Layout

'''
see README.md
'''

class EditCells():

  def __init__(self, options):

    self.requested = {
      'shape': options.shape,
      'shape_size': options.size,
      'shape_facing': options.facing,
      'top': options.top,
      'stroke_width': options.width
    }
    self.bg = options.bg

  def update(self, svg, layer, draw):
    message = None
    elem = svg.selection.first() # assume that first in ElementList is <g />
    searchId = elem.get('id')
    #shapes = svg.getElementById(searchId)
    shapes = draw.get_elems_by_id(svg, searchId)[0]

    if self.requested['shape'] == 'triangle' and self.requested['shape_size'] == 'large':
      message = 'Large triangles are not possible, ignoring this request.'
    elif shapes is not None:
      # update the background style, but only if we're given a new value
      bg = draw.set_background(searchId, self.bg, svg) 
      draw.set_foreground(shapes, self.requested)
      elem.style['stroke-width'] = svg.unittouu(self.requested['stroke_width'])
      # add the top elems last
      if self.requested['top']:
        draw.sort_groups(searchId, svg, layer) # TODO why two SVGs
    else:
      message = f"group id={searchId} not found"
    return message

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
    draw = Draw([layout.size, layout.width, layout.height])

    if self.svg.selection: #  and self.is_recurrence():
      e = EditCells(self.options)
      message = e.update(self.svg, layer, draw)
      if message:
        self.msg(message)
    else:
      self.msg("After opening up a model you have to select a cell for editing")

if __name__ == '__main__':
  Recurrink().run()
