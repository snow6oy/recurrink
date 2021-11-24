#!/usr/bin/env python3

import getopt, sys, csv, os, pprint, hmac, json

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

  def make(self, model=None):
    ''' unpack the model(s) into a json database 
    '''
    if model and model in self.models: # for dry run
      # print(f"model {model} ok")
      fn = f"./{model}.json"
      data = {}
      data[model] = {
        'id': self.models[model]['id'],
        'size': self.models[model]['size'],
        'cells': self.get_cells(model)
      }
    elif not model and len(self.models):
      # print(f"all models ok")
      fn = "./recurrink.json"
      data = {}
      for m in self.models:
        data[m] = {
          'id': self.models[m]['id'],
          'size': self.models[m]['size'],
          'cells': self.get_cells(m)
        }
    else:
      raise KeyError(f"no such model: {model}")

    with open(fn, "w") as outfile:
      json.dump(data, outfile, indent=2)

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
  def get_model_list(self):
    html = str()
    for m in self.models:
      html += f"        <option value=\"{m}\">{m}</option>\n"
    return html

  def get_digest(self, model, row):
    secret = b'model'
    to_digest = ''.join(row)
    digest_maker = hmac.new(secret, to_digest.encode('utf-8'), digestmod='MD5')
    digest = digest_maker.hexdigest()
    return digest

class Layout:
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

  def add(self, model, db=None):
    ''' load database of all models or use given db'''
    if db is None:
      json_file = './recurrink.json'
      with open(json_file) as f:
        db = json.load(f)

    if model in db:
      self.get = db[model]
    else:
      raise ValueError("unknown model {model}")
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

  def render(self, draw, group, strokeWidth):
    '''
    draw out a model by repeating blocks across the canvas
    '''
    for paintOrder in range(2):
      for y in range(self.maxRows):
        ySizeMm = self.yOffset + (y * self.size)
        for x in range(self.maxCols):
          xSizeMm = self.xOffset + (x * self.size)
          cell = self.get_cell_by_position(x, y)
          data = self.get_cell(cell)
          if not data:
            continue # checker-board background !
          gid = f"{cell}{paintOrder}"
          sid = f"{cell}{paintOrder}-{x}-{y}"
 
          if paintOrder:
            shape = draw.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method here
            group[gid].add(shape) 
          else:
            shape = draw.backgrounds(cell, xSizeMm, ySizeMm)
            shape.set_id(sid)    # calling an inkex method
            group[gid].add(shape)
          ''' support for top is missing in recurrink 
          if gid in strokeWidth:
            data['stroke_width'] = strokeWidth[gid]  # TODO test stroke width and top
          elif paintOrder == 2 and data['top']:   # last in paint order appears on top
            shape = draw.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method here
            group[gid].add(shape) 
          elif paintOrder == 1 and not data['top']:
            shape = draw.shape(cell, xSizeMm, ySizeMm, data)
            shape.set_id(sid)    # calling an inkex method
            group[gid].add(shape) 
          '''
    return None

###############################################################################
def usage():
  message = '''
-m MODEL        name of model to build
-a              build all models
-l	        model list in web format
'''
  print(message)

def main():
  '''
  get inputs from command line
  '''
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hm:al", ["help", "model="])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  model = None
  all_models = False
  list_only = False
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
    else:
      assert False, "unhandled option"
    # ...
  return (model, all_models, list_only)

if __name__ == '__main__':
  ''' TODO add support for friendly name
    ./configure -m tumbao 
  '''
  (model, all_models, list_only) = main()
  pp = pprint.PrettyPrinter(indent=1)
  if (model or all_models):
    b = Builder()
    b.make(model)
  elif (list_only):
    b = Builder()
    print(b.get_model_list())
  else:
    usage()
