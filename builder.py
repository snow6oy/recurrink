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

class Builder:
  ''' read and write data to file
      will replace Builder once new filesystem and data model is done
  '''
  def __init__(self, model, machine=False):
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
      self.author = 'MACHINE' if machine else 'HUMAN'
      self.uniq = self.uniq_cells()
    else:
      raise KeyError(f"model '{model}' has no entry in models")

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

  def write_rinkfile(self, view=None):
    if view:
      fn = f"/tmp/{view}.rink"
      data = self.load_rinkdata(view)
    else:
      fn = f"/tmp/{self.model}.rink"
      data = self.load_rinkdata(self.model)
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

    fn = self.get_digest(cellvalues) if self.author == 'MACHINE' else self.model
    #self.write_json(f"{self.datadir}/{model}/{fn}.json", source)
    self.write_json(f"/tmp/{fn}.json", jsondata)
    return fn

  #####################################################################
  ######################### p r i v a t e #############################

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

  def get_cellvalues(self, cell):
    data = self.read_tmp_csvfile()
    valstr = None
    for d in data:
      if (cell == d[0]):
        valstr = ' '.join(d)
        break
    return valstr
###############################################################################
def usage():
  message = '''
-l list models
-m MODEL --output CSV  [--random]
-m MODEL --output JSON [--random]
-m MODEL --output RINK [--view VIEW]
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

  (model, output, cell, view, ls, rand) = (None, None, None, None, False, False)
  for opt, arg in opts:
    if opt in ("-o", "--output") and arg in ('RINK', 'CSV', 'JSON'):
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
      rand = True
    else:
      assert False, "unhandled option"
  return (model, output, cell, view, ls, rand)

if __name__ == '__main__':
  (model, output, cell, view, ls, rand) = inputs()
  ''''''''''''''''''''''''''''''''''''''''''
  if model:
    b = Builder(model, machine=rand)
    if output == 'CSV':                   # create tmp csv file containing a collection of random cell values
      print(b.write_csvfile())            # OR default vals for humans. return cell vals a b c d
    elif cell:                            # lookup values by cell return as comma-separated string '1,square,north'
      print(b.get_cellvalues(cell)) 
    elif view:                            # write RINK with VIEW.json as source
      print(b.write_rinkfile(view=view))
    elif output == 'JSON':                # convert tmp csv into json as permanent record 
      print(b.write_jsonfile())           # write json and return digest
    elif output == 'RINK':                # combine CSV and JSON as RINK for inkscape to convert to SVG
      print(b.write_rinkfile())
    else:
      usage()
  elif ls:
    print("\n".join(Builder.list_model(None, '/home/gavin/Pictures/artWork/recurrences'))) # bit of a hack
  else:
    usage()
