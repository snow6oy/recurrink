#!/usr/bin/env python3

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
    s = stream.read() # slurp the stream 
    data = s.decode() # convert to string
    cells = tf.read(model, txt=data) # convert string to dict
    #l = Layout(model, factor=float(self.options.scale))
    l = Layout(model)
    # prepare A4 document but with pixels for units
    doc = self.get_template(width=l.width, height=l.height, unit='px')
    svg = self.add_metadata(doc, model, self.options)
    # group, cells = l.build(data, svg)
    group = l.build(cells, svg)
    l.render(group, cells)
    return doc

  def add_metadata(self, doc, model, scale):
    ''' namspeces work when they feel like it so we avoid them like the plague
    '''
    svg = doc.getroot()
    svg.namedview.set('inkscape:document-units', 'px')
    svg.set('recurrink-id', model)
    svg.set('recurrink-factor', scale)
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

  def write(self, model, keys, celldata):
    expectedsize = len(self.header)
    with open(f"/tmp/{model}.txt", 'w') as f:
      print(' '.join(self.colnam), file=f)
      for i, data in enumerate(celldata):
        vals = [str(d) for d in data] # convert everything to string
        vals.insert(0, keys[i])
        if len(vals) != expectedsize:
          raise ValueError(f"{model}.txt has {len(vals)} not {expectedsize}\n{vals}")
        line = ' '.join(vals)
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
  parser_r.add_argument("-v", "--view", help='hex name with 32 char', required=True)
  parser_i = subparsers.add_parser('init', help='set config for new image')
  parser_i.add_argument('-m', '--model', help='name of base model')
  parser_i.add_argument("-v", "--view", help='view to clone')
  parser_c = subparsers.add_parser('commit', help='write immutable entry to db')
  parser_c.add_argument('-m', '--model', help='name of base model')
  parser_c.add_argument("-a", "--author", choices=['human', 'machine'])
  parser_c.add_argument("-s", "--scale", type=float, default=1.0, help='range of 0.5 to 2.0 ish')
  #  pars.add_argument("--control",  default=0, help="Control 0-9 zero is random")
  parser_d = subparsers.add_parser('delete')
  parser_d.add_argument("-v", "--view", help='view to remove from db')
  parser_u = subparsers.add_parser('update', help='update svg from config')
  parser_u.add_argument('-m', '--model', help='name of model to update', required=True)
  return parser.parse_args()

def stats():
  ''' pretty list of models
  '''
  return m.get(output='stats')              

def info(digest):
  ''' accept a view id e.g. c364ab54ff542adb322dc5c1d6aa4cc8
      return view meta data for publisher to use
  '''
  view = v.get(digest=digest)
  return " ".join(view)

# TODO stop losting control :-D
# control should be written as view metadata 
# but we generate the digest much later

# TODO when model is none glob *.txt and source model from /tmp

# TODO call update
def init(model=None, digest=None):
  ''' after init create SVG by calling svgfile
  '''
  print(model, digest)
  if digest:
    control = 5
    #model, celldata = v.clone(digest)
    return 'not implemented'
  elif model:
    control = 3
    celldata = v.create(model)
  else:
    control = 0
    model, celldata = v.create(rnd=True)
  b = Blocks(model)
  tf.write(model, b.cells(), celldata)
  # update(model)
  return model
 
# TODO add scale and control as params
#   '--scale', str(scale), 
def update(model, scale=1.0):
  Input().run([
    '--output', f'/tmp/{model}.svg', 
    f'/tmp/{model}.txt'
  ])
  return model

def delete(view):
  return view if v.delete(view) else 'not deleted'

# TODO celldata is not being saved
def commit(model, scale, author):
  ''' read config, write to database and return digest
  '''
  celldata = tf.read(model, output=list())
  if v.set(model, tf.digest, author):
    [c.set(tf.digest, row[0], row) for row in celldata]
    return tf.digest
  else:
    return 'unknown error'
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
if __name__ == '__main__':
  tf = TmpFile()
  args = inputs()
  if (args.keyword == 'list'):
    print(stats())
  elif (args.keyword == 'read'):
    print(info(args.view))
  elif (args.keyword == 'init'):
    print(init(model=args.model, digest=args.view))
  elif (args.keyword == 'commit'):
    # TODO why collect scale here? it is part of Model not View
    print(commit(args.model, args.scale, args.author))
  elif (args.keyword == 'delete'):
    print(delete(args.view))
  elif (args.keyword == 'update'):
    print(update(args.model))
  '''
  the 
  end
  '''
