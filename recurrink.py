#!/usr/bin/env python3

import sys
import random
import getopt
import hmac
from db import Views, Models, Cells, Blocks
from svgfile import SvgFile

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

  def read(self, model):
    ''' read text file, convert values from string to primitives and sort on top
        > a square medium north False #FFF #CCC 1.0 #000 0 0 1.0
        return a dictionary keyed by cell
    '''
    sortdata = list()
    cells = dict()
    to_hash = str()
    with open(f"/tmp/{model}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    # cell shape size facing top fill bg fo stroke sw sd so

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
    return cells

  def set(self, key):
    ''' make a digest that has a unique value for each model view
    '''
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()

class SvgFile:
  def update(self, celldata, scale=None):
    pass
  def create(self, model, control):
    pass

def usage():
  message = '''
--list 
--init   [-m MODEL -v VIEW]
--update [-m MODEL -s SCALE]
--commit [-m MODEL -s SCALE -a AUTHOR]
'''
  print(message)

def inputs():
  ''' get inputs from command line
  '''
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:s:a:v:", ["init", "update", "commit", "list"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  control = {
    'init'  : False,
    'update': False, 
    'commit': False, 
    'list':   False, 
    'model':  None,
    'scale':  None,
    'author': None,
    'view':   None
  }
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt == '--init':
      control['init'] = True
    elif opt == '--update':
      control['update'] = True
    elif opt == '--commit':
      control['commit'] = True
    elif opt in ("--list"):
      control['list'] = True
    elif opt == "-a" and arg in ('human', 'machine'):
      control['author'] = arg
    elif opt == "-v" and len(arg) == 32:
      control['view'] = arg
    elif opt == "-s" and float(arg):
      control['scale'] = arg
    elif opt == "-m":
      control['model'] = arg
    else:
      assert False, "unhandled option"
  return control

def init(model=None, digest=None):
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
  svg.create(model, control)
  svg.update(celldata)
  # TODO create rink.pid
 
def update(model, scale):
  scale = 1.0 if scale is None else 1.0
  if model is None:
    model = 'soleares'  # TODO check for rink.pid
  celldata = tf.read(model)
  svg.update(celldata, scale) 

def commit(model, scale, author):
  celldata = tf.read(model)
  v.update(tf.digest, scale, author)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
if __name__ == '__main__':
  control = inputs()
  v = Views()
  m = Models()
  tf = TmpFile()
  svg = SvgFile()
  if control['list']:
    print(m.get(output='stats'))              # pretty list of models
  elif control['init']:                       # generate TXT and SVG files in tmp
    init(model=control['model'], digest=control['view']) 
  elif control['update']:                     # copy from TXT to SVG
    update(control['model'], control['scale'])
  elif control['commit']:                     # copy from TXT to DB 
    commit(control['model'], control['scale'], control['author'])
  else:
    usage()
  '''
  the 
  end
  '''
