#!/usr/bin/env python3

import sys
import random
import getopt
import hmac
from db import Views, Models, Cells, Blocks

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

  def read(self, model, txt=None):
    ''' read text file, convert values from string to primitives and sort on top
        > cell shape size facing top fill bg fo stroke sw sd so
        > a square medium north False #FFF #CCC 1.0 #000 0 0 1.0
        return a dictionary keyed by cell
    '''
    sortdata = list()
    cells = dict()
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
    for d in sortdata:
      z = zip(self.header, d)
      attrs = dict(z)
      cell = attrs['cell']
      del attrs['cell']
      cells.update({cell: attrs})
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

  ''' should be a function of TmpFile
  def getcells(self, model, txt=None):
    header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    cells = dict()
    if txt:
      print(f"str {txt}")
    else:
      print(f"modl {model}")
    linedata = self.get_text(txt) if txt else self.get_file(model)
    #[linedata.append(line.split()) for line in txt.splitlines()]
    #del linedata[0] # remove header
    for d in linedata:
      d[4] = (d[4] in ['True', 'true'])
      d[9] = int(d[9])
      d[10] = int(d[10])
    for d in linedata:
      z = zip(header, d)
      attrs = dict(z)
      cell = attrs['cell']
      del attrs['cell']
      cells.update({cell: attrs})
    return cells
  '''

  def set(self, key):
    ''' make a digest that has a unique value for each model view
    '''
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()

def usage():
  message = '''
--list 
--init   [-m MODEL -v VIEW]
--update [-m MODEL -s SCALE]
--commit [-m MODEL -s SCALE -a AUTHOR]
'''
  print(message)

class Options:
 
  def __init__(self):
    self.init  = False
    self.commit= False 
    self.list  = False 
    self.delete= False 
    self.read  = False
    self.model = None
    self.scale = None
    self.author= None
    self.view  = None

def inputs():
  ''' get inputs from command line
  '''
  options = Options()
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:s:a:v:", ["init", "delete", "commit", "list", "read"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt == '--init':
      options.init = True
    elif opt == '--update':
      options.update = True
    elif opt == '--commit':
      options.commit = True
    elif opt == ("--list"):
      options.list = True
    elif opt == ("--read"):
      options.read = True
    elif opt == "-a" and arg in ('human', 'machine'):
      options.author = arg
    elif opt == "-v" and len(arg) == 32:
      options.view = arg
    elif opt == "-s" and float(arg):
      options.scale = arg
    elif opt == "-m":
      options.model = arg
    else:
      assert False, "unhandled option"
  return options

def init(model=None, digest=None):
  ''' after init create SVG by calling svgfile
  '''
  if digest:
    control = 5
    model, celldata = v.clone(digest)
  elif model:
    control = 3
    celldata = v.create(model)
  else:
    control = 0
    model, celldata = v.create(rnd=True)
  b = Blocks(model)
  tf.write(model, b.cells(), celldata)
  # svg.create(model, control)
  # svg.update(celldata)
  # TODO create rink.pid HERE and ditch bash script
 
def update(model, scale):
  ''' update by calling svgfile.py directly
  '''
  pass

def commit(model, scale, author):
  celldata = tf.read(model)
  v.update(tf.digest, scale, author)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
if __name__ == '__main__':
  options = inputs()
  m = Models()
  v = Views()
  tf = TmpFile()
  if options.list:
    print(m.get(output='stats'))              # pretty list of models
  elif options.init:                       # generate TXT and SVG files in tmp
    init(model=options.model, digest=options.view) 
  elif options.commit:                     # copy from TXT to DB 
    commit(options.model, options.scale, options.author)
  elif options.read: # read accepts a view value e.g. c364ab54ff542adb322dc5c1d6aa4cc8
    view = v.get(digest=options.view)
    print(" ".join(view) + "\n")
  elif options.delete:
    view.delete(options.view)
  else:
    usage()
  '''
  the 
  end
  '''

