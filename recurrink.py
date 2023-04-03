#!/usr/bin/env python3
# coding=utf-8

import inkex
from inkex import Group, Circle, Rectangle, Polygon, TextElement
import getopt, sys, csv, os, hmac, json, math

class Draw:
  ''' use viewer to do the maths to render a cell
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

  def __init__(self):
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
    self.models = self.load_models()

  def write_rink_file(self, model, data):
    fn = f"models/{model}.rink"
    with open(fn, "w") as outfile:
      json.dump(data, outfile, indent=2)

  def make(self, model=None):
    ''' unpack the model(s) into a json database 
    '''
    if model and model in self.models: # for dry run
      # print(f"model {model} ok")
      data = {}
      data = {
        'id': self.models[model]['id'],
        'size': self.models[model]['size'],
        'cells': self.get_cells(model)
      }
      self.write_rink_file(model, data)

    elif not model and len(self.models):
      # print(f"all models ok")
      data = {}
      for m in self.models:
        data[m] = {
          'id': self.models[m]['id'],
          'size': self.models[m]['size'],
          'cells': self.get_cells(m)
        }
        self.write_rink_file(m, data[m])

    else:
      raise KeyError(f"no such model: {model}")

    return None

  def get_positions(self, model):
    ''' 
    positions link the model and cell: for example 
    csv with a line a, x, x a will appear in json as { a: { positions: [[0,0], [3,0] }}
    '''
    positions = dict()
    for row_num, row in enumerate(self.models[model]['csv']):
      for col_num, col in enumerate(row):
        if col not in positions:
          positions[col] = list()
        coord = (col_num, row_num)
        positions[col].append(coord)

    return positions

  def get_cells(self, model):
    '''
    '''
    if model in self.models:
      positions = self.get_positions(model)
      cells = self.models[model]['json']
      for p in positions:
        cells[p]['positions'] = positions[p]
    else:
      raise KeyError(f"model '{model}' has no entry in models")

    return cells

  def load_models(self):
    models = {}
    conf = []

    for root, dir, files in os.walk('./models'):
      conf.extend(files)

    for f in conf:
      (m, ext) = f.split('.')  # this.that
      # print(m, ext)
      if m not in models:
        models[m] = dict()
      if ext == 'csv':
        csvData = self.load_model(m)
        models[m]['csv'] = csvData
        models[m]['size'] = (len(csvData[0]), len(csvData))
        models[m]['id'] = self.get_digest(m, models[m]['csv'][0])
      elif ext == 'json':
        json_file = f"./models/{m}.json"
        models[m]['json'] = self.load_view(json_file)
      elif ext == 'rink':
        pass # leave for inkscape
      else:
        raise ValueError(f"Unknown config {ext}")

    return models

  def load_model(self, model):
    '''
    load csv data
    '''
    model_csv = f"./models/{model}.csv"
    # print("load model " + model_csv)
    with open(model_csv) as f:
      reader = csv.reader(f, delimiter=' ')
      data = list(reader)
    return data

  def list_cells(self, model):
    ''' send mondrian the robot a list of uniq cells``
    '''
    seen = dict()
    for row in self.load_model(model):
      for cell in row:
        seen[cell] = seen[cell] + 1 if cell in seen else 0
    return ' '.join(seen.keys())

  def load_view(self, json_file):
    #print("load view  " + json_file)
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
  def _get_model_list(self):
    modelList = str()
    for m in self.models:
      modelList += f"{m}\n"
    return modelList

  def get_model_list(self):
    modelList = str()
    ranked = dict()
    for m in self.models:
      numCells = len(self.models[m]['json'].keys())
      blockWidth = self.models[m]['size'][0]
      blockHeight = self.models[m]['size'][1]
      rank = (numCells * blockWidth * blockHeight)
      ranked[m] = rank
    # sort according to rank
    sortRank = {k: v for k, v in sorted(ranked.items(), key=lambda item: item[1])}
    for m in sortRank:
      modelList += f"{sortRank[m]:{4}} {m}\n"
    return modelList

  def get_digest(self, model, row):
    secret = b'model'
    to_digest = ''.join(row)
    digest_maker = hmac.new(secret, to_digest.encode('utf-8'), digestmod='MD5')
    digest = digest_maker.hexdigest()
    return digest

###############################################################################
def usage():
  message = '''
-m MODEL        generate a rink file for named model
-c MODEL        list cells in named model
-a              build all rink files
-l	        list models, simplest first
'''
  print(message)

def main():
  '''
  get inputs from command line
  '''
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hm:c:al", ["help", "model="])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  model = None
  all_models = False
  list_only = False
  list_cells = False
  for o, a in opts:
    if o == "-a":
      all_models = True
    elif o in "-l":
      list_only = True
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-m", "--model"):
      model = a
    elif o in ("-c", "--model"):
      list_cells = True
      model = a
    else:
      assert False, "unhandled option"
    # ...
  return (model, all_models, list_only, list_cells)

if __name__ == '__main__':
  ''' recurrink cli
  '''
  (model, all_models, list_only, list_cells) = main()
  if (list_cells):
    b = Builder()
    print(b.list_cells(model))
  elif (model or all_models):
    b = Builder()
    b.make(model)
  elif (list_only):
    b = Builder()
    print(b.get_model_list())
  else:
    usage()
