#!/usr/bin/env python3
# coding=utf-8

import os
import sys
import csv
import json
import glob
import hmac
import math
import random
import getopt
import inkex
from inkex import Group, Circle, Rectangle, Polygon, TextElement

class Draw:
  ''' does the maths to render a cell
  '''
  def __init__(self, baseUnit):
    ''' units must be in sync with Layout.sizeUu 
    '''
    self.sizeUu  = baseUnit[0] # size
    self.x_offset = baseUnit[1] # x offset
    self.y_offset = baseUnit[2] # y offset

  def backgrounds(self, cell, x, y):
    ''' the first cell painted onto the grid is a filled rectangle
        see Builder for a list of the available colours
    '''
    w = str(self.sizeUu)
    h = str(self.sizeUu)
    bg = Rectangle(x=str(x), y=str(y), width=w, height=h)
    return bg

  def shape(self, cell, X, Y, a):
    ''' create a shape from a cell for adding to a group
    '''
    if a['shape'] == 'circle':
      s = self.set_circle(cell, X, Y, a)
    elif a['shape'] == 'line':
      s = self.set_line(cell, X, Y, a)
    elif a['shape'] == 'square':
      s = self.set_square(cell, X, Y, a)
    elif a['shape'] == 'triangle':
      s = self.set_triangle(cell, X, Y, a)
    else:
      s = self.set_text(a['shape'], X, Y)

    return s

  def set_circle(self, cell, X, Y, a):
    halfw = a['stroke_width'] / 2
    fullw = a['stroke_width']

    if a['shape_size'] == 'large': 
      size = self.sizeUu / 2
      sum_two_sides = (size**2 + size**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - halfw
    elif a['shape_size'] == 'medium':
      r = (self.sizeUu / 2 - halfw) # normal size
    else:
      raise ValueError(f"Cannot set circle <{cell}> to {a['shape_size']} size")

    x = str(X + self.sizeUu / 2)
    y = str(Y + self.sizeUu / 2)
    circle = Circle(cx=x, cy=y, r=str(r))
    #circle.label = cell
    return circle

  def set_line(self, cell, X, Y, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    a['shape_facing'] = 'north' if a['shape_facing'] == 'south' else a['shape_facing']
    a['shape_facing'] = 'east' if a['shape_facing'] == 'west' else a['shape_facing']

    if a['shape_size'] == 'large' and a['shape_facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y - self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
    elif a['shape_size'] == 'large' and a['shape_facing'] == 'east':
      x      = str(X - self.sizeUu / 3 + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str((self.sizeUu / 3 * 2 + self.sizeUu) - fullw)
      height = str(self.sizeUu / 3 - fullw)
    elif a['shape_size'] == 'medium' and a['shape_facing'] == 'north':
      x      = str(X + self.sizeUu / 3 + halfw)
      y      = str(Y + halfw)
      width  = str(self.sizeUu / 3 - fullw)
      height = str(self.sizeUu - fullw)
    elif a['shape_size'] == 'medium' and a['shape_facing'] == 'east':
      x      = str(X + halfw)
      y      = str(Y + self.sizeUu / 3 + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu / 3 - fullw)
    else:
      raise ValueError(f"Cannot set {cell} to {a['shape_size']}")

    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def set_square(self, cell, xSizeMm, ySizeMm, a):
    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2
      
    if a['shape_size'] == 'medium':
      x      = str(xSizeMm + halfw)
      y      = str(ySizeMm + halfw)
      width  = str(self.sizeUu - fullw)
      height = str(self.sizeUu - fullw)
    elif a['shape_size'] == 'large':
      third  = self.sizeUu / 3
      x      = str(xSizeMm - third / 2 + halfw)
      y      = str(ySizeMm - third / 2 + halfw)
      width  = str(self.sizeUu + third - fullw)
      height = str(self.sizeUu + third - fullw)
    else:
      raise ValueError("Cannot set rectangle {}".format(cell))

    rect = Rectangle(x=x, y=y, width=width, height=height)
    return rect

  def set_triangle(self, cell, X, Y, a):

    fullw = a['stroke_width']
    halfw = a['stroke_width'] / 2 # stroke width is halved for repositioning

    if a['shape_facing'] == 'west': 
      points = [
        X + fullw, Y + self.sizeUu / 2, 
        X + self.sizeUu - halfw, Y + fullw, 
        X + self.sizeUu - halfw, Y + self.sizeUu - fullw,
        X + fullw, Y + self.sizeUu / 2
      ]
    elif a['shape_facing'] == 'east': 
      points = [
        X + halfw, Y + fullw, 
        X + self.sizeUu - fullw, Y + self.sizeUu / 2,
        X + halfw, Y + self.sizeUu - fullw,
        X + halfw, Y + fullw
      ]
    elif a['shape_facing'] == 'north': 
      points = [
        X + fullw, Y + self.sizeUu - halfw,
        X + self.sizeUu / 2, Y + fullw,
        X + self.sizeUu - fullw, Y + self.sizeUu - halfw,
        X + fullw, Y + self.sizeUu - halfw
      ]
    elif a['shape_facing'] == 'south':
      points = [
        X + halfw, Y + halfw, 
        X + self.sizeUu / 2, Y + self.sizeUu - fullw, 
        X + self.sizeUu - halfw, Y + halfw,
        X + halfw, Y + halfw
      ]
    else:
      raise ValueError("Cannot face triangle {}".format(a['shape_facing']))
    
    polyg = Polygon(points=",".join(map(str, points)))
    #polyg.label = cell
    return polyg
  
  def set_text(self, shape, X, Y):
    ''' when the shape is unknown print as text in the cell
    '''
    x = str(X + 3)
    y = str(Y + 40)
    textElement = TextElement(x=x, y=y)
    textElement.text = shape
    # self.debug(textElement)
    return textElement

class Layout(Draw):
  ''' expand cells provided by Draw across a canvas
  '''
  def __init__(self, factor=1.0):
    ''' 
    original calculation was page size 210 x 297 mm (A4 portrait)
    since unit are not millimeters this table is inaccurate

    factor    size   col  row   x os   y os
      0.5     24.0     7   11   21.0   16.5  twice as big
      1.0     12.0    15   22   15.0   16.5  do nothing
      2.0      6.0    30   44   15.0   16.5  half size
    '''
    self.width   = 1122.5197  # px
    self.height  = 793.70081
    self.size    = (48 / factor)  
    self.maxCols = int(22 * factor)
    self.maxRows = int(15 * factor)  # num of row  
    numOfMargins = 2
    self.xOffset = (self.width  - (self.maxCols * self.size)) / numOfMargins # 33.25985000000003
    self.yOffset = (self.height - (self.maxRows * self.size)) / numOfMargins # 36.85040500000002
    super().__init__([self.size, self.xOffset, self.yOffset])

  def add(self, model, db=None):
    ''' load database of named model or use given db'''
    if db is None:
      json_file = f"models/{model}.rink"
      with open(json_file) as f:
        db = json.load(f)
      self.get = db
    elif db:
      self.get = db
    else: 
      raise ValueError(f"cannot find model {model}. db len is {len(db)}")
    return self.get

  def get_cell(self, cell):
    if cell in self.get['cells']:
      return self.get['cells'][cell]
    else:
      raise KeyError(f"unknown cell {cell}")

  def uniq_cells(self):
    ''' provide a unique list of cells using in the model 
    '''  
    return list(self.get['cells'].keys())

  def blocksize(self):
    '''
    send the model co-ordinate range as a tuple
    '''
    blocksize = self.get['size']
    return tuple(blocksize)

  def get_id(self):
    '''
     lookup a digest such as 3e8539a9929c0b2595f44146f1b3770c
    '''
    return self.get['id']

  def get_cell_by_position(self, x, y):
    '''
    repeat the block to fit the canvas
    1. calculate the block number using integer division, blocksize and counter
    2. then new counter = counter - blocknumber * blocksize
    '''
    cell = None
    (x_blocksize, y_blocksize) = self.blocksize()

    y_blocknum = int(y / y_blocksize)
    Y = y - (y_blocknum * y_blocksize)

    x_blocknum = int(x / x_blocksize)
    X = x - (x_blocknum * x_blocksize)
    #print(f'xy({x}, {y})  XY({X}, {Y})  blocknum({x_blocknum}, {y_blocknum})')
    current_posn = (X, Y) # tuples are immutable

    for c in self.get['cells']:
      for p in self.get['cells'][c]['positions']:
        posn = tuple(p)
        if posn == current_posn:
          cell = c
          break
    return cell

  def blocknum_to_uu(self, xBlocknum, yBlocknum):
    ''' convert a position in the grid to pixels 
    '''
    xUu = self.xOffset + (xBlocknum * self.size)
    yUu = self.yOffset + (yBlocknum * self.size)
    return xUu, yUu

  #def render(self, draw, group, strokeWidth):
  def render(self, group, strokeWidth):
    ''' draw out a model by repeating blocks across the canvas
    '''
    # TODO the algorithm should follow JSON 
    for paintOrder in range(2):
      for y in range(self.maxRows):
        for x in range(self.maxCols):
          (xSizeMm, ySizeMm) = self.blocknum_to_uu(x, y)
          cell = self.get_cell_by_position(x, y)
          data = self.get_cell(cell)
          if not data:
            continue # checker-board background !
          gid = f"{cell}{paintOrder}"
          sid = f"{cell}{paintOrder}-{x}-{y}"
 
          if paintOrder:
            shape = self.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method here
            group[gid].add(shape) 
          else:
            shape = self.backgrounds(cell, xSizeMm, ySizeMm)
            shape.set_id(sid)    # calling an inkex method
            group[gid].add(shape)
    return None

class Builder:
  ''' read and write data to file
      will replace Builder once new filesystem and data model is done
  '''
  def __init__(self, model, machine=False):
    self.workdir = '/home/gavin/Pictures/artWork/recurrences' # paths are relative to working dir
    models = self.list_model() 
    if model in models:
      self.model = model

      self.attributes = {
        'shape':'square',
        'shape_size':'medium',
        'shape_facing':'north',
        'fill': '#fff', 
        'bg': '#ccc',
        'fill_opacity':1.0, 
        'stroke':'#000', 
        'stroke_width': 0, 
        'stroke_dasharray': 0,
        'stroke_opacity':1.0,
        'top':False
      }

      self.header = ['cell', 'model'] + list(self.attributes.keys())
      # self.header = [ 'cell','model','shape', 'size', 'facing', 'bg', 'width', 'top' ]
      self.author = 'MACHINE' if machine else 'HUMAN'
      self.uniq = self.uniq_cells()
    elif model:
      raise ValueError(f"unknown {model}")

  #################################################################
  ################ p u b l i c ####################################

  def write_csvfile(self):
    ''' generate a config as cell x values matrix
        for humans copy default values over
        but machines get randoms
    '''
    init = dict()
    for c in self.uniq: 
      randomvals = self.random_cellvalues(c) if self.author == 'MACHINE' else dict()
      row = list()
      row.append(c)
      row.append(self.model)
      for a in self.attributes:
        if a in randomvals:
          row.append(randomvals[a])
        else:
          row.append(self.attributes[a])
      init[c] = row

    cells = self.write_tmp_csvfile(f"/tmp/{self.model}.csv", init)
    return cells

  def write_rinkfile(self, json_file=None):
    ''' rink input can be JSON from HUMAN or MACHINE
        output is always same 
    '''
    if json_file is None:
      json_file = f"/tmp/{self.model}.json"
    data = self.load_rinkdata(json_file)
    self.write_json(f"/tmp/{self.model}.rink", data)

  def write_jsonfile(self):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")

    digest = self.get_digest(cellvalues) # if self.author == 'MACHINE' else self.model
    self.write_json(f"/tmp/{self.model}.json", jsondata)
    return digest

  def find_recurrence(self, file, ext):
    ''' expected file structure
        soleares/
        ├── h
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.json
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.svg 
    '''
    paths = glob.glob(f'*/*/{file}.{ext}')
    if paths:
      return paths
    else:
      raise FileNotFoundError(f"{file}.{ext}")

  def list_model(self):
    os.chdir(self.workdir)
    return next(os.walk('.'))[1]

  def list_model_with_stats(self):
    print(f"uniq    x    y model")
    print('-' * 80)
    for m in self.list_model():
      self.model = m
      index_csv = self.load_model()
      (x, y) = (len(index_csv[0]), len(index_csv))
      print(f"{len(self.uniq_cells()):>4} {x:>4} {y:>4} {m}")

  #####################################################################
  ######################### p r i v a t e #############################

  def write_tmp_csvfile(self, fn, celldata):
    cells = self.uniq
    with open(fn, 'w') as f:
      wr = csv.writer(f, quoting=csv.QUOTE_NONE)
      wr.writerow(self.header)
      [wr.writerow(celldata[c]) for c in cells]
    return ' '.join(cells)

  def uniq_cells(self):
    ''' send mondrian the robot a list of uniq cells 
    '''
    seen = dict()
    for row in self.load_model():
      for cell in row:
        seen[cell] = seen[cell] + 1 if cell in seen else 0
    return seen.keys()

  def load_model(self):
    ''' load csv data
    '''
    csvfile = f"{self.model}/index.csv"
    # print("load model " + csvfile)
    with open(csvfile) as f:
      reader = csv.reader(f, delimiter=' ')
      data = list(reader)
    return data

  def load_view(self, json_file):
    '''
    TODO check that bg: values match
      '#FFA500':'orange', 
      '#DC143C':'crimson', 
      '#CD5C5C':'indianred', 
      '#C71585':'mediumvioletred', 
      '#4B0082':'indigo', 
      '#32CD32':'limegreen', 
      '#9ACD32':'yellowgreen',
      '#000':'black',
      '#fff':'white',
      '#ccc':'gray'
    '''
    # print("load view  " + json_file)
    with open(json_file) as f:
      conf = json.load(f)
      init = {}
      for cell in conf:
        init[cell] = dict()
        for a in self.attributes:
          if a in conf[cell]:
            init[cell][a] = conf[cell][a]  # use value from json
          else:
            init[cell][a] = self.attributes[a] # default
    return init

  def random_cellvalues(self, cell):
    ''' TODO these attributes were supposed to be updated interactively 
        to expose them for randomisation, first need to update effect.py
      'fill': '#fff',
      'fill_opacity':1.0,
      'stroke':'#000',
      'dash': 0,
      'opacity':1.0, '''
    rnd = dict()
    # default 'shape':'square',
    rnd['shape'] = random.choice(["circle", "line", "square", "triangle"])
    rnd['shape_facing'] = random.choice(["north", "south", "east", "west"])
    # default 'shape_size':'medium',
    sizes = ["medium", "large"]
    if rnd['shape'] == "triangle":
      rnd['shape_size'] = "medium"
    else:
      rnd['shape_size'] = random.choice(sizes)
    rnd['top'] = str(random.choice([True, False]))
    rnd['bg'] = random.choice(["orange","crimson","indianred","mediumvioletred","indigo","limegreen","yellowgreen","black","white","gray"])
    rnd['stroke_width'] = str(random.choice(range(10)))
    # fill stroke opacity dash
    rnd['fill'] = random.choice(["#fff","#ccc","#CD5C5C","#000","#FFA500","#DC143C","#C71585","#4B0082","#32CD32","#9ACD32"])
    rnd['fill_opacity'] = random.choice(['0.1', '0.4', '0.7', '1.0', '1.0', '1.0'])
    rnd['stroke'] = random.choice(["#fff","#ccc","#CD5C5C","#000","#FFA500","#DC143C","#C71585","#4B0082","#32CD32","#9ACD32"])
    rnd['stroke_dasharray'] = str(random.choice(range(10)))
    return rnd

  def write_json(self, fn, data):
    with open(fn, "w") as outfile:
      json.dump(data, outfile, indent=2)

  def convert_row2cell(self, data):
    ''' sample input 
   [[ 'a','soleares','triangle','3','west','medium','yellowgreen','False' ],
    [ 'b','soleares','circle','8','west','large','orange','True' ],
    [ 'c','soleares','line','6','south','medium','gray','True' ]] '''

    source = dict()
    to_hash = str()
    for d in data:
      #z = zip(header, data[i])
      to_hash += ''.join(d)
      z = zip(self.header, d)
      row = dict(z)
      cell = row['cell']
      model = row['model']
      # pad missing values with default
      for a in self.attributes:
        row[a] = self.attributes[a] if a not in row else row[a] 
      source.update({cell: { 
                   'shape': row['shape'],
              'shape_size': row['shape_size'],
            'shape_facing': row['shape_facing'],
                    'fill': row['fill'], 
                      'bg': row['bg'],
            'fill_opacity': row['fill_opacity'], 
                  'stroke': row['stroke'], 
            'stroke_width': int(row['stroke_width']),
        'stroke_dasharray': row['stroke_dasharray'],
          'stroke_opacity': row['stroke_opacity'],
                     'top': bool(row['top'])
      }})
    return (model, to_hash, source)

  def get_digest(self, cellvalues):
    ''' hashkey should have a unique value for each model view
    '''
    secret = b'self.model'
    key = ''.join(cellvalues)
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    return digest_maker.hexdigest()

  def load_rinkdata(self, view):
    ''' unpack the model(s) into a json database 
    '''
    model_data = self.load_model()
    json_data = self.load_view(view)
    if (len(json_data.keys()) != len(self.uniq)):
      raise KeyError(f"missing cells: {view}")

    return {
        'id': self.model,
        'size': (len(model_data[0]), len(model_data)),
        'cells': self.get_cells(model_data, json_data)
    }

  def get_cells(self, model_data, json_data):
    ''' combine model and view data to optimise SVG build process
    '''
    positions = self.get_positions(model_data)
    for p in positions:
      json_data[p]['positions'] = positions[p]
    return json_data

  def get_positions(self, model_data):
    ''' positions link the model and cell: for example 
        csv with a line a, x, x a will appear in json as { a: { positions: [[0,0], [3,0] }}
    '''
    positions = dict()
    for row_num, row in enumerate(model_data):
      for col_num, col in enumerate(row):
        if col not in positions:
          positions[col] = list()
        coord = (col_num, row_num)
        positions[col].append(coord)

    return positions

  def get_cellvalues(self, cell):
    data = self.read_tmp_csvfile()
    valstr = None
    for d in data:
      if (cell == d[0]):
        valstr = ' '.join(d)
        break
    return valstr

  def read_tmp_csvfile(self):
    with open(f"/tmp/{self.model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)
    return data

###############################################################################
def usage():
  message = '''
-l list models
-m MODEL --output CSV  [--random]
-m MODEL --output JSON [--random]
-m MODEL --output RINK [--view VIEW]
-m MODEL --output CELL
-m MODEL --cell CELL
'''
  print(message)

def inputs():
  ''' get inputs from command line
  '''
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:o:c:v:lr", ["model=", "output=", "cell=", "view=", "list", "random"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  (model, output, cell, view, ls, rnd) = (None, None, None, None, False, False)
  for opt, arg in opts:
    if opt in ("-o", "--output") and arg in ('RINK', 'CSV', 'JSON', 'CELL', 'SVG'):
      output = arg
    elif opt in ("-c", "--cell"):
      cell = arg
    elif opt in ("-v", "--view"):
      view = arg
    elif opt in ("-m", "--model"):
      model = arg
    elif opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-l", "--list"):
      ls = True
    elif opt in ("-r", "--random"):
      rnd = True
    else:
      assert False, "unhandled option"
  return (model, output, cell, view, ls, rnd)

if __name__ == '__main__':
  (model, output, cell, view, ls, rnd) = inputs()
  ''''''''''''''''''''''''''''''''''''''''''
  b = Builder(model, machine=rnd)
  if model:
    if output == 'CSV':                   # create tmp csv file containing a collection of random cell values
      print(b.write_csvfile())            # OR default vals for humans. return cell vals a b c d
    elif view and output == 'RINK':       # write RINK with Library json as source
      b.write_rinkfile(json_file=view)
    elif output == 'RINK':                # write RINK with MODEL.json as source
      b.write_rinkfile()
    elif output == 'JSON':                # convert tmp csv into json as permanent record 
      print(b.write_jsonfile())           # write json and return digest
    elif output == 'CELL':                # get a list of uniq cells
      print(' '.join(b.uniq)) 
    elif cell:                            # lookup values by cell return as comma-separated string '1,square,north'
      print(b.get_cellvalues(cell)) 
    else:
      usage()
  elif ls:
    #print("\n".join(b.list_model()))      # has side effect of setting workdir
    b.list_model_with_stats()               # has side effect of setting workdir
  elif view and output == 'JSON':         # query db
    print(b.find_recurrence(view, 'json')[0])
  elif view and output == 'SVG':          # lookup SVG
    print(b.find_recurrence(view, 'svg')[0])
  else:
    usage()
  '''
    elif view:                            # write RINK with VIEW.json as source
      print(b.write_rinkfile(view=view))
  '''
