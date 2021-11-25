#!/usr/bin/env python3

import re
import json
import inkex
from configure import Layout
from draw import Draw
from inkex import Group

#from inkex.base import SvgOutputMixin
#from inkex.elements import TextElement

# TODO can we sub-class Layout ? class Model(SvgOutputMixin):
class Model():

  def __init__(self, model, layout):
    ''' options set model name and scale '''
    self.layout = layout
    self.model = model

  # def build(self, svg):
  def make(self, data, svg):
    ''' Generate an svg document for given model '''
    cells = self.layout.add(self.model, data)
    if not cells: # is model with given name available from db ?
      raise ValueError(f'not found <{model}>')

    groups_to_create = self.layout.uniq_cells()
    group = {}  # hold a local reference to groups created in svg doc
    strokeWidth = {}
    sw0 = svg.unittouu(0) # hide the cracks between the background tiles

    for g in groups_to_create:
      # draw background  cells
      bg = Group()
      bg.set_id(f'{g}0')
      bg.style = { 'fill' : self.layout.get_cell(g)['bg'], 'stroke-width': sw0, 'stroke':'#fff' }
      group[f'{g}0'] = bg # local copy
      svg.add(bg)
      # draw foreground cells
      fg = Group()
      sw1 = svg.unittouu(self.layout.get_cell(g)['stroke_width'])
      fg.set_id(f'{g}1') 
      fg.style = {
        'fill'            : self.layout.get_cell(g)['fill'],
        'fill-opacity'    : self.layout.get_cell(g)['fill_opacity'],
        'stroke'          : self.layout.get_cell(g)['stroke'],
        'stroke-width'    : sw1,
        'stroke-dasharray': self.layout.get_cell(g)['stroke_dasharray'],
        'stroke-opacity'  : self.layout.get_cell(g)['stroke_opacity']
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
        self.options.input_file e.g. /home/gavin/recurrink/arpeggio.rink
    '''
    #size = 48 # cell dimension 
    #width = 1122.5197  # px
    #height = 793.70081
    fn = re.findall(r"([^\/]*)\.", self.options.input_file)
    doc = None

    if fn is None:
      raise ValueError(f"bad file {self.options.input_file}")
    else:
      s = stream.read() # slurp the stream 
      data = json.loads(s) # create a json object
      # TODO check if scale has to be float() and pass it in once defined in INX
      #scale = 1.0 if 'scale' not in self.options else self.options.scale
      layout = Layout()
      draw = Draw([layout.size, layout.width, layout.height])
      # prepare A4 document but with pixels for units
      doc = self.get_template(width=layout.width, height=layout.height, unit='px')
      svg = doc.getroot()
      svg.namedview.set('inkscape:document-units', 'px')
      # generate the model from config
      m = Model(fn[0], layout) # filename without ext 
      group, strokeWidth = m.make(data, svg)
      layout.render(draw, group, strokeWidth)

    return doc

if __name__ == '__main__':
  Input().run()
