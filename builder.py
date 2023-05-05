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

class Builder2:
  ''' read and write data to file
      will replace Builder once new filesystem and data model is done
  '''
  def __init__(self, model, author=None):
    models = self.list_model('/home/gavin/Pictures/artWork/recurrences') # paths are relative to working dir
    if model in models:
      self.model = model
      self.attributes = {
        'shape':'square',
        'size':'medium',
        'facing':'north',
        'fill': '#fff', 
        'bg': '#ccc',
        'fillopacity':1.0, 
        'stroke':'#000', 
        'width': 0, 
        'dash': 0,
        'dashopacity':1.0,
        'top':False
      }
      self.header = ['cell', 'model'] + list(self.attributes.keys())
      # self.header = [ 'cell','model','shape', 'size', 'facing', 'bg', 'width', 'top' ]
      self.author = 'human' if author else 'machine'
      self.uniq = self.uniq_cells()
    else:
      raise KeyError(f"model '{model}' has no entry in models")

  #### Public ####

  def write_csvfile(self):
    ''' generate a config as cell x values matrix
        for humans copy default values over
        but machines get randoms
    '''
    init = dict()
    for c in self.uniq: 
      rando = self.random_cellvalues(c) if self.author == 'machine' else dict()
      row = list()
      row.append(c)
      row.append(self.model)
      for a in self.attributes:
        if a in rando:
          row.append(rando[a])
        else:
          row.append(self.attributes[a])
      init[c] = row

    cells = self.write_tmp_csvfile(f"/tmp/{self.model}.csv", init)
    return cells

  def write_rinkfile(self, view):
    fn = f"/tmp/{self.model}.rink"
    data = self.load_rinkdata(view)
    self.write_json(fn, data)
    return fn

  # def create_new_view(self, cell_data):
  def write_jsonfile(self):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")

    fn = self.get_digest(cellvalues)
    #self.write_json(f"{self.datadir}/{model}/{fn}.json", source)
    self.write_json(f"/tmp/{fn}.json", jsondata)
    return fn

  #### Private ####
  ''' get digest
    d = self.load_model()
    fn = self.get_digest(self.model, d[0])
  '''
  def list_model(self, datadir):
    os.chdir(datadir)
    return next(os.walk('.'))[1]

  def write_tmp_csvfile(self, fn, celldata):
    cells = self.uniq
    with open(f"/tmp/{self.model}.csv", 'w') as f:
      wr = csv.writer(f, quoting=csv.QUOTE_NONE)
      wr.writerow(self.header)
      [wr.writerow(celldata[c]) for c in cells]
    return ' '.join(cells)

  def read_tmp_csvfile(self):
    with open(f"/tmp/{self.model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)
    return data

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
    #csvfile = f"{self.datadir}/{self.model}/index.csv"
    csvfile = f"{self.model}/index.csv"
    # print("load model " + csvfile)
    with open(csvfile) as f:
      reader = csv.reader(f, delimiter=' ')
      data = list(reader)
    return data

  def load_view(self, view):
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
    json_file = self.find_recurrence(view, 'json')[0]
    #print(findview('550d193efe80f67e92d5a0c59ad9d354'))
    print("load view  " + json_file)
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

  def find_recurrence(self, file, ext):
    ''' expected file structure
        soleares/
        ├── h
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.json
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.svg 
    '''
    paths = glob.glob(f'*/*/{file}.{ext}')
    return paths

  def random_cellvalues(self, cell):
    ''' TODO these attributes were supposed to be updated interactively 
        to expose them for randomisation, first need to update effect.py
      'fill': '#fff',
      'fill_opacity':1.0,
      'stroke':'#000',
      'dash': 0,
      'opacity':1.0, '''
    rando = dict()
    # default 'shape':'square',
    rando['shape'] = random.choice(["circle", "line", "square", "triangle"])
    rando['facing'] = random.choice(["north", "south", "east", "west"])
    # default 'shape_size':'medium',
    sizes = ["medium", "large"]
    if rando['shape'] == "triangle":
      rando['size'] = "medium"
    else:
      rando['size'] = random.choice(sizes)
    rando['top'] = str(random.choice([True, False]))
    rando['bg'] = random.choice(["orange","crimson","indianred","mediumvioletred","indigo","limegreen","yellowgreen","black","white","gray"])
    rando['width'] = str(random.choice(range(10)))
 
    return rando

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
      source.update({cell: { 
        'shape': row['shape'],
        'width': int(row['width']),
        'facing':row['facing'],
        'size': row['size'],
        'bg': row['bg'],
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
        'view': view,
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

  ######### REFACTOR after this ####################################
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
      rank = (numCells + blockWidth + blockHeight)
      ranked[m] = rank
    # sort according to rank
    sortRank = {k: v for k, v in sorted(ranked.items(), key=lambda item: item[1])}
    for m in sortRank:
      modelList += f"{sortRank[m]:{4}} {m}\n"
    return modelList

class Mondrian(Builder2):
  ''' extend builder to support Mondrian The Robot
  '''
  def __init__(self):
    self.header = [ 'id','output','shape','width','facing','size','bg','top' ]
    super().__init__()

  def get_cellvalues(self, model, cell):
    data = m.read_tmp_csvfile(model)
    valstr = None
    for d in data:
      if (cell == d[0]):
        valstr = ' '.join(d)
        break
    return valstr


  ######################### p r i v a t e #############################
  def write_json_file(self, model, fn, data):
    f = f"{self.json_dir}/{model}/{fn}.json"
    with open(f, "w") as outfile:
      json.dump(data, outfile, indent=2)

  def create_from_log(self, csvfile):
    ''' this function is already obsolete
        but it might be useful to troubleshoot /tmp/model.csv 
    '''
    data = self.read_tmp_csvfile('./mondrian.log')
    model = None
    counter = 0

    for i, d in enumerate(data):
      if model and model != data[i][1]:
        start = i - counter
        (model, to_hash, source) = self.convert_row2cell(data[start:i])
        print(model, to_hash)
        self.update_digest(model, to_hash)
        self.write_json_file(model, self.models[model]['id'], source)
        counter = 0
      model = data[i][1]
      counter += 1


###############################################################################
def usage():
  message = '''
-m MODEL --output CSV|JSON|RINK
-m MODEL --cell CELL
-l list models, simplest first
'''
  print(message)

def inputs():
  ''' get inputs from command line
  '''
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:o:c:d:l", ["model=", "output=", "cell=", "digest=", "list"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  model = None
  cell = None
  digest = None
  output = None
  ls = False
  for opt, arg in opts:
    if opt in ("-o", "--output") and arg in ('RINK', 'CSV', 'JSON'):
      output = arg
    elif opt in ("-c", "--cell"):
      cell = arg
    elif opt in ("-d", "--digest"):
      digest = arg
    elif opt in ("-m", "--model"):
      model = arg
    elif opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-l", "--list"):
      ls = True
    else:
      assert False, "unhandled option"
  return (model, output, cell, digest, ls)

if __name__ == '__main__':
  b = Builder()
  m = Mondrian()
  (model, output, cell, digest, ls) = inputs()
  ''''''''''''''''''''''''''''''''''''''''''''
  if output == 'CSV':                         # create tmp csv file containing a collection of random cell values
    print(m.write_tmp_csvfile(model))         # return cell vals a b c d
  elif cell:                                  # lookup values by cell return as comma-separated string '1,square,north'
    print(m.get_cellvalues(model, cell)) 
  elif digest:                                # write RINK with source digest.json
    print(b.make(model=model, id=digest))
  elif output == 'JSON':                      # convert tmp csv into json as permanent record 
    csvdata = m.read_tmp_csvfile(model)
    print(m.create_new_view(csvdata))     # write json and return digest
  elif output == 'RINK':                      # combine CSV and JSON as RINK for inkscape to convert to SVG
    print(b.make(model=model))
  elif (ls):
    print(b.get_model_list())
  else:
    usage()
