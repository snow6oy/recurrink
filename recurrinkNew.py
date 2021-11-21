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

  def __init__(self, svg, options):

    elem = svg.selection.first() # assume that first in ElementList is <g />
    self.searchId = elem.get('id')
    self.requested = {
      'shape': options.shape,
      'shape_size': options.size,
      'shape_facing': options.facing,
      'top': options.top,
      'stroke_width': int(options.width)
    }
    self.bg = self.options.bg
    self.svg = svg

  def update(self, draw):
    message = None
    shapes = draw.get_elems_by_id(self.svg, self.searchId)[0]
    if requested['shape'] == 'triangle' and requested['shape_size'] == 'large':
      message = 'Large triangles are not possible, ignoring this request.'
    elif shapes is not None:
      # update the background style, but only if we're given a new value
      bg = draw.set_background(self.searchId, self.bg, self.svg) 
      draw.set_foreground(shapes, requested)
      elem.style['stroke-width'] = svg.unittouu(self.options.width)
      # add the top elems last
      if requested['top']:
        draw.sort_groups(self.searchId, self.svg, svg) # TODO where is svg coming from ?
      else:
        self.msg(f"group id={self.searchId} not found")
    return message

class Recurrink(inkex.EffectExtension):
  ''' draw recurring patterns using inkscape '''
  def add_arguments(self, pars):
    pars.add_argument("--tab", type=str, dest="tab")
    pars.add_argument("--model",  default='bakerstwelve', help="Place a model on canvas")
    pars.add_argument("--scale",  default=1.0, help="Scale in or out (0.5 - 2.0)")
    pars.add_argument("--shape",  default='square', help="Replace one shape with another")
    pars.add_argument("--size",  default='normal', help="Increase shape size (not triangles)")
    pars.add_argument("--facing",  default='north', help="Rotate shapes (not squares or circles)")
    pars.add_argument("--width",  default=0, help="Border thickness as a number 0-9")
    pars.add_argument("--bg",  default='#FFFFFF', help="Change the background colour")
    pars.add_argument("--top",  type=inkex.Boolean, default=False, help="Stay on top when overlapping")

  def is_recurrence(self):
    ''' 
      add a tag to the SVG doc e.g. recurrence="v1"
      in order to sequence processing of the input parameters
    '''
    root = self.svg.root
    ok = True if 'recurrence' in root.attrib and root.attrib['recurrence'] == self.version else False
    return ok

  def base_unit(self, svg):
    '''
      set the base user units. all subsequent dimensions are relative to them
    '''
    size = svg.unittouu(48)  # cell dimension
    x = svg.unittouu(60)     # margin width
    y = svg.unittouu(64)     # margin height
    return (size, x, y)

  def effect(self):  # effect because generate is a subset
    ''' check if svg is a recurrence and then apply inputs
    '''
    self.version = 'v1'
    svg = self.svg.get_current_layer()
    layout = Layout(self.base_unit(svg))
    base_unit = layout.set_scale(float(self.options.scale)) # adjust base units according to input
    draw = Draw(base_unit)

    if self.svg.selection and self.is_recurrence():
      e = EditCells(self.svg, self.options)
      message = e.update(draw)
      if message:
        self.msg(message)
    elif (self.is_recurrence()):
      self.msg("After opening up a model you have to select a cell for editing")
    elif self.options.model: 
      # generate the initial model from config
      cells = layout.add(self.options.model)
      if not cells: # is model with given name available from db ?
        raise ValueError(f'error loading {self.options.model}')
      groups_to_create = layout.uniq_cells()
      group = {}  # keep local copy of newly created groups because easier than coding in xpath!
      strokeWidth = {} 
      sw0 = svg.unittouu(0) # hide the cracks between the background tiles

      for g in groups_to_create:
        # TODO draw.background(g)
        bg = Group()
        bg.set_id(f'{g}0')
        bg.style = { 'fill' : layout.get_cell(g)['bg'], 'stroke-width': sw0, 'stroke':'#fff' }
        group[f'{g}0'] = bg # local copy
        svg.add(bg)

        # TODO draw.foreground(g)
        fg = Group()
        sw1 = svg.unittouu(layout.get_cell(g)['stroke_width'])
        fg.set_id(f'{g}1') 
        fg.style = {
          'fill'            : layout.get_cell(g)['fill'],
          'fill-opacity'    : layout.get_cell(g)['fill_opacity'],
          'stroke'          : layout.get_cell(g)['stroke'],
          'stroke-width'    : sw1,
          'stroke-dasharray': layout.get_cell(g)['stroke_dasharray'],
          'stroke-opacity'  : layout.get_cell(g)['stroke_opacity']
        }
        group[f'{g}1'] = fg
        strokeWidth[f'{g}1'] = sw1  # adjust cell dimension according to stroke width
        svg.add(fg)

      self.svg.root.set('recurrence', self.version) # TODO use id (digest) from conf
      layout.render(draw, group, strokeWidth)
    else:
      self.msg("nothing to do")

if __name__ == '__main__':
  Recurrink().run()

