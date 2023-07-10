#!/usr/bin/env python3

import os
import argparse
import re
import pprint
import inkex
import sys
import random
import hmac
from db import Views, Models, Cells, Blocks
from svgfile import Layout

pp = pprint.PrettyPrinter(indent=2)
m = Models()
v = Views()
c = Cells()

class Input(inkex.InputExtension):
  ''' create a model SVG from a txt file /tmp/MODEL.txt
      model, and scale SHOULD be written in SVG metadata
      
      NICE to have would be add portrait as input options
  '''
  def load(self, stream):
    ''' inkscape passes in a stream from io.BufferedReader
        self.options.input_file is immutable and must exist or FileNotFoundError is raised
    '''
    doc = None
    fn = re.findall(r"([^\/]*)\.", self.options.input_file) # filename without ext 
    model = fn[0]
    # print(model, CONTROL)
    s = stream.read() # slurp the stream 
    data = s.decode() # convert to string
    cells = tf.read(model, txt=data) # convert string to dict
    l = Layout(model, CONTROL)
    # prepare A4 document but with pixels for units
    doc = self.get_template(width=l.width, height=l.height, unit='px')
    svg = self.add_metadata(doc, model, l.factor)
    print(f"factor {l.factor} control {l.control}")
    l.transform(cells)
    # TODO stop passing cells to build and render 
    group = l.build(svg)
    l.render(group)
    return doc

  def add_metadata(self, doc, model, factor):
    ''' namspeces work when they feel like it so we avoid them like the plague
    '''
    svg = doc.getroot()
    svg.namedview.set('inkscape:document-units', 'px')
    svg.set('recurrink-id', model)
    svg.set('recurrink-factor', factor)
    return svg
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class TmpFile():
  ''' read and write data to /tmp
  '''
  def __init__(self):
    self.colnam = ['cell','shape','size','facing','top','fill','bg','fo','stroke','sw','sd','so']
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]

  def write(self, model, keys, celldata, celltype=dict()):
    ''' accept cells as list or dict and write them to a space-separated text file
    '''
    expectedsize = len(self.header)
    with open(f"/tmp/{model}.txt", 'w') as f:
      print("\t".join(self.colnam), file=f)
      for i, data in enumerate(celldata):
        vals = [str(d) for d in data] # convert everything to string
        if isinstance(celltype, dict): 
          vals.insert(0, keys[i])     # push the dict key into the list
        if len(vals) != expectedsize:
          raise ValueError(f"{model}.txt has {len(vals)} not {expectedsize}\n{vals}")
        line = "\t".join(vals)
        #line = ' '.join(vals)
        print(line, file=f)

  def read(self, model, txt=None, output=dict()):
    ''' read text file, convert values from string to primitives and sort on top
        > cell shape size facing top fill bg fo stroke sw sd so
        > a square medium north False #FFF #CCC 1.0 #000 0 0 1.0
        return a dictionary keyed by cell
    '''
    cells = None
    sortdata = list()
    to_hash = str()
    data = self.get_text(txt) if txt else self.get_file(model)

    for d in data:
      to_hash += ''.join(d)
      d[4] = (d[4] in ['True', 'true'])
      d[9] = int(d[9])
      d[10] = int(d[10])
    self.set(to_hash)
    # sort them so that top:true will be rendered last
    sortdata = sorted(data, key=lambda x: x[4])

    if isinstance(output, list):
      cells = data
    elif isinstance(output, dict):
      cells = dict()
      for d in sortdata:
        z = zip(self.header, d)
        attrs = dict(z)
        cell = attrs['cell']
        del attrs['cell']
        cells.update({cell: attrs})
    else:
      raise TypeError(f"unsupported type {output}")
    if not cells: # is model with given name available from db ?
      raise ValueError(f'non readable <{model}>')
    return cells

  def get_file(self, model):
    with open(f"/tmp/{model}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    return data

  def get_text(self, text):
    data = list()
    [data.append(line.split()) for line in text.splitlines()]
    del data[0] # remove header
    return data

  def set(self, key):
    ''' make a digest that has a unique value for each model view
    '''
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def inputs():
  ''' get inputs from command line
  '''
  parser = argparse.ArgumentParser(prog='recurrink')
  subparsers = parser.add_subparsers(dest='keyword', help='sub-command help')
  parser_l = subparsers.add_parser('list', help='list models in db')
  parser_r = subparsers.add_parser('read', help='get view metadata')
  parser_r.add_argument('-m', '--model', help='name of base model')
  parser_r.add_argument("-v", "--view", help='hex name with 32 char')
  parser_i = subparsers.add_parser('init', help='set config for new image')
  parser_i.add_argument('-m', '--model', help='name of base model')
  parser_i.add_argument("-v", "--view", help='view to clone')
  parser_c = subparsers.add_parser('commit', help='write immutable entry to db')
  parser_c.add_argument('-m', '--model', help='name of base model')
  parser_c.add_argument("-a", "--author", choices=['human', 'machine'])
  parser_c.add_argument("-c", "--control",  default='00', help="Control is a two digest code 00-99")
  parser_d = subparsers.add_parser('delete')
  parser_d.add_argument("-v", "--view", help='view to remove from db')
  parser_u = subparsers.add_parser('update', help='update svg from config')
  parser_u.add_argument('-m', '--model', help='name of model to update', required=True)
  parser_u.add_argument("-c", "--control",  default='00', help="Control is a two digest code 00-99")
  return parser.parse_args()

def stats():
  ''' pretty list of models
  '''
  #return m.get(output='stats')              
  return m.stats()

def info(model=None, digest=None):
  ''' accept a view id e.g. c364ab54ff542adb322dc5c1d6aa4cc8
      return view meta data for publisher to use
      OR a pretty text visualation of a model
  '''
  out = str()
  if model:
    posdata = m.positions('koto')
    for row in posdata:
      for col in row:
        out += col + ' '
      out += "\n"
  elif digest:
    view = v.read(digest=digest)
    out = " ".join(view[:2])
  else:
    pass # expected either a model or digest as input but whatever ..
  return out

# TODO when model is none glob *.txt and source model from /tmp
# TODO call update
def init(model=None, digest=None):
  ''' after init create SVG by calling svgfile
  '''
  ct = dict()
  control = 0
  if digest:
    celldata = v.read(digest=digest, celldata=True, output=list())
    model, _, control = v.read(digest=digest)
    ct = list() # configure TmpFile to write from a list
  elif model:
    _, celldata = v.generate(model=model)
  else:
    model, celldata = v.generate(rnd=True)
  b = Blocks(model)
  tf.write(model, b.cells(), celldata, celltype=ct)
  # update(model)
  return model if not control else f"{model} {control}"
 
def update(model, control):
  ''' send inputs from to inkex with argparse and Layout() as a global
      inkex creates an SVG file and its name is printed to screen
  '''
  global CONTROL
  CONTROL = control
  output, input_file = f'/tmp/{model}.svg', f'/tmp/{model}.txt'
  Input().run(['--output', output, input_file]) # inkex argparse
  print()
  return output

# TODO think about the orphaned styles
# and dont ferrget the rinks
def delete(view):
  return view if v.delete(view) else 'not deleted'

def commit(model, control, author):
  ''' read config, write to database and return digest
  '''
  workdir = 'rinks'
  pubdir = 'pubq'
  celldata = tf.read(model, output=list())
  response = 'unknown error'
  if v.create(model, tf.digest, author, control=control):
    [c.create(tf.digest, row) for row in celldata]
    if os.path.isfile(f"/tmp/{model}.svg"):
      svgname = f"{workdir}/{model}/{tf.digest}.svg"
      os.rename(f"/tmp/{model}.svg", svgname)
      os.symlink(f"../{svgname}", f"{pubdir}/{tf.digest}.svg")
      # TODO rm /tmp/model.txt
      response = svgname
    else:
      raise FileNotFoundError(f"{model}.svg not found in /tmp")
  return response
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
if __name__ == '__main__':
  tf = TmpFile()
  args = inputs()
  if (args.keyword == 'list'):
    print(stats())
  elif (args.keyword == 'read'):
    print(info(model=args.model, digest=args.view))
  elif (args.keyword == 'init'):
    print(init(model=args.model, digest=args.view))
  elif (args.keyword == 'commit'):
    print(commit(args.model, args.control, args.author))
  elif (args.keyword == 'delete'):
    print(delete(args.view))
  elif (args.keyword == 'update'):
    print(update(args.model, args.control))
  '''
  the 
  end
  '''
