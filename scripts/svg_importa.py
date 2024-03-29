#!/usr/bin/env python3

''' convert SVG to /tmp/VIEW.csv 
'''
import csv
import inkex
import pprint
from inkex import Group, load_svg
from recurrink import Builder

pp = pprint.PrettyPrinter(indent=2)

class BuilderMate(Builder):

  def __init__(self, model):
    ''' options set model name and scale 
    '''
    super().__init__(model=model)

class Input(inkex.OutputExtension):

  def add_arguments(self, pars):
    pars.add_argument("--model",  default=None, help="Model name for /tmp/MODEL.csv")

  def save(self, stream):
    #print(self.options.output)
    print("-" * 80)

    if self.model is None:
      print(' '.join(list(self.view.keys())))
      pp.pprint(self.view)
    else:
      bm = BuilderMate(self.model) 
      print(self.model)
      print(' '.join(list(bm.uniq)))

      csvdata = dict()
      for cell in bm.uniq:
        row = list()
        row.append(cell)
        row.append(self.model)
        for a in bm.attributes:
          if a in self.view[cell]:
            row.append(self.view[cell][a])              # dashes and underscores :/
          elif a == 'fill_opacity' and 'fill-opacity' in self.view[cell]:
            row.append(self.view[cell]['fill-opacity'])
          elif a == 'stroke_width' and 'stroke-width' in self.view[cell]:
            row.append(self.view[cell]['stroke-width'])
          elif a == 'stroke_dasharray' and 'stroke-dasharray' in self.view[cell]:
            row.append(self.view[cell]['stroke-dasharray'])
          elif a == 'stroke_opacity' and 'stroke-opacity' in self.view[cell]:
            row.append(self.view[cell]['stroke-opacity'])
          else:
            row.append(bm.attributes[a])
        csvdata[cell] = row

      bm.write_tmp_csvfile(f"/tmp/{self.model}.csv", csvdata)
    '''
      fg.set_id(f'{g}1') 
      fg.style = {
        'fill'            : self.get_cell(g)['fill'],
        'fill-opacity'    : self.get_cell(g)['fill_opacity'],
        'stroke'          : self.get_cell(g)['stroke'],
        'stroke-width'    : sw1,
        'stroke-dasharray': self.get_cell(g)['stroke_dasharray'],
        'stroke-opacity'  : self.get_cell(g)['stroke_opacity']
      }
    '''
  def add_style(self, fb, cell, line):
    ''' foreground = fg cell = x 
        line = fill:#40e0d0;fill-opacity:1;stroke:#000000;stroke-width:0;stroke-dasharray:none;stroke-opacity:1
    '''
    style = dict()
    styles = line.split(';')
    for s in styles:
      (k, v) = s.split(':')
      k = 'bg' if fb == 'bg' else k
      self.view[cell][k] = v

  def add_style_from_elem(self, fb, shape, el):
    ''' shape shape_size shape_facing fill bg fill_opacity stroke stroke_width stroke_dasharray stroke_opacity top
        uniq count of each cell attrib '''
    #print(fb, shape, el.tag_name)
    cell = el.tag_name
    for s in ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-opacity']:
      if s in el.attrib:
        cell = ':'.join([cell, el.attrib[s]])
    if cell not in self.view:
      self.view[cell] = 1
    else:
      self.view[cell] += 1


  def zzadd_style_from_elem(self, fb, shape, el):
    k = el.attrib['id'] + el.attrib['fill']
    if k not in self.uniq:
      self.uniq[k] = chr(self.az)
      self.az += 1
    cell = self.uniq[k]
    if cell not in self.view:
      self.view[cell] = dict()
    self.view[cell]['shape'] = shape
    for s in ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-opacity']:
      if s in el.attrib:
        self.view[cell][s] = el.attrib[s]

  def query_shape(self, s):
    ''' create a list of strings
        shape_name, shape_facing, shape_size
    '''
    shape = ['', '', '']
    if s.tag_name == 'rect':
      # TODO shape_size print(s.attrib['width'])
      if int(s.attrib['width']) == int(s.attrib['height']):
        shape[0] = 'square' 
        shape[1] = 'north' 
      elif int(s.attrib['width']) > int(s.attrib['height']):
        shape[0] = 'line' 
        shape[1] = 'east' 
      elif int(s.attrib['width']) < int(s.attrib['height']):
        shape[0] = 'line' 
        shape[1] = 'north' 
    elif s.tag_name == 'polygon':
      p = s.attrib['points'].split(',')
      if p[1] == p[5]:
        shape[1] = 'north'
      elif p[0] == p[4]:
        shape[1] = 'east'
      elif p[2] == p[4]:
        shape[1] = 'west'
      else:
        shape[1] = 'south'
      shape[0] = 'triangle'
    else:
      shape[0] = s.tag_name
      shape[1] = 'north' 
    return shape

  def add_shape(self, attrib_id, el):
    a = attrib_id.split('-')
    if a[0] == 'fg':
      cell = a[1]
      if cell in self.view and 'shape' not in self.view[cell]:
        self.view[cell]['shape'] = self.query_shape(el)[0]
        self.view[cell]['shape_facing'] = self.query_shape(el)[1]
        print(f"{cell} : {self.view[cell]['shape']} {self.view[cell]['shape_facing']}")

  def load(self, stream):
    ''' inkex passes us a json file as a stream
    '''
    self.model = None if 'model' not in self.options else self.options.model
    self.view = dict()
    self.uniq = dict()
    self.az = 97             # start the cell counter at a
    doc = load_svg(stream)
    x = doc.getroot()    #print(x.attrib['width'])
    if not len(x):
      raise ValueError('empty svg')

    for g in x:
      if g.tag_name != 'g':
        continue
      # print(g.tag_name) 
      for tag in g:  # top layer
        #print(' ' * 1, root.attrib['id'], root.attrib['style'])
        idvals = tag.attrib['id'].split('-')
        if len(idvals) == 1:
          cell = idvals[0]
          if tag.attrib['id'] == 'bg':
            fb = 'bg'
          else:
            fb = 'fg'
        elif len(idvals) == 2:
          (fb, cell) = idvals
        if cell not in self.view:
          self.view[cell] = dict()
        if 'style' in tag.attrib:
          self.add_style(fb, cell, tag.attrib['style'])
        else:
          self.add_style_from_elem(fb, cell, tag)
        [self.add_shape(el.attrib['id'], el) for el in tag]
    print(self.uniq)

if __name__ == '__main__':
  Input().run()
