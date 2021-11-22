#!/usr/bin/env python3

import re
import json
import inkex
from inkex.base import SvgOutputMixin
from inkex.elements import TextElement
from inkex import Group

class Model(SvgOutputMixin):
  def __init__(self, model_name):
    ''' options set model name and scale '''
    self.model_name = model_name

  def make(self, data, svg):
    ''' Generate an svg document for given model '''
    textElement = TextElement()
    g = Group()
    layer = svg.get_current_layer()
    svgId = data[self.model_name]['id']
    textElement.text = f"model {self.model_name} id {svgId}"
    g.add(textElement)
    layer.add(g)
    return svg

class Loader(inkex.InputExtension):

  # TODO add scale and portrait as input options
  def load(self, stream):
    ''' inkscape passes us a json file as a stream
        self.options.input_file e.g. /home/gavin/recurrink/tumbao.rce
    '''
    fn = re.findall(r"([^\/]*)\.", self.options.input_file)
    doc = None

    if fn is None:
      raise ValueError(f"bad file {self.options.input_file}")
    else:
      m = Model(fn[0]) # filename without ext 
      s = stream.read() # slurp the stream 
      data = json.loads(s) # create a json object
      # prepare A4 document but with pixels for units
      doc = self.get_template(width=1122.5197, height=793.70081, unit='px')
      svg = doc.getroot()
      svg.namedview.set('inkscape:document-units', 'px')
      svg = m.make(data, svg)

    return doc

  def effect(self):
    pass

if __name__ == '__main__':
  Loader().run()

