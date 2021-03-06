#!/usr/bin/env python3

import re
import json
import inkex
from inkex import Group
from recurrink import Layout

class Model(Layout):

  def __init__(self, model, factor=None):
    ''' options set model name and scale 
    '''
    super().__init__(factor=float(factor))
    self.model = model

  # def build(self, svg):
  def make(self, data, svg):
    ''' Generate an svg document for given model '''
    cells = self.add(self.model, data)
    if not cells: # is model with given name available from db ?
      raise ValueError(f'not found <{model}>')

    groups_to_create = self.uniq_cells()
    group = {}  # hold a local reference to groups created in svg doc
    strokeWidth = {}
    sw0 = svg.unittouu(0) # hide the cracks between the background tiles

    for g in groups_to_create:
      # draw background  cells
      bg = Group()
      bg.set_id(f'{g}0')
      bg.style = { 'fill' : self.get_cell(g)['bg'], 'stroke-width': sw0, 'stroke':'#fff' }
      group[f'{g}0'] = bg # local copy
      svg.add(bg)
      # draw foreground cells
      fg = Group()
      sw1 = svg.unittouu(self.get_cell(g)['stroke_width'])
      fg.set_id(f'{g}1') 
      fg.style = {
        'fill'            : self.get_cell(g)['fill'],
        'fill-opacity'    : self.get_cell(g)['fill_opacity'],
        'stroke'          : self.get_cell(g)['stroke'],
        'stroke-width'    : sw1,
        'stroke-dasharray': self.get_cell(g)['stroke_dasharray'],
        'stroke-opacity'  : self.get_cell(g)['stroke_opacity']
      }
      group[f'{g}1'] = fg
      strokeWidth[f'{g}1'] = sw1  # adjust cell dimension according to stroke width
      svg.add(fg)
      
    return group, strokeWidth

class Input(inkex.InputExtension):
  ''' create a model SVG from a config file
  '''
  # TODO add portrait as input options
  def add_arguments(self, pars):
    pars.add_argument("--scale",  default=1.0, help="Scale in or out (0.5 - 2.0)")

  def load(self, stream):
    ''' inkscape passes us a json file as a stream
        self.options.input_file e.g. recurrink/models/arpeggio.rink
    '''
    fn = re.findall(r"([^\/]*)\.", self.options.input_file) # filename without ext 
    doc = None

    if fn is None:
      raise ValueError(f"bad file {self.options.input_file}")
    else:
      s = stream.read() # slurp the stream 
      data = json.loads(s) # create a json object
      scale = 1.0 if 'scale' not in self.options else self.options.scale
      m = Model(fn[0], factor=float(scale))
      # prepare A4 document but with pixels for units
      doc = self.get_template(width=m.width, height=m.height, unit='px')
      svg = self.add_metadata(doc, data['id'], scale)
      group, strokeWidth = m.make(data, svg)
      m.render(group, strokeWidth) # generate the model from the rink file

    return doc

  def add_metadata(self, doc, rinkId, factor):
    ''' namspeces work when they feel like it so we avoid them like the plague
    '''
    svg = doc.getroot()
    svg.namedview.set('inkscape:document-units', 'px')
    svg.set('recurrink-id', rinkId)
    svg.set('recurrink-factor', factor)
    return svg

if __name__ == '__main__':
  Input().run()
