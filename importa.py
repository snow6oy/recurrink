#!/usr/bin/env python3
# coding=utf-8

import os
import csv
import json
import glob
from recurrink import Db

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
        'shape_facing':None,
        'fill': '#FFF', 
        'bg': '#CCC',
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

  def find_recurrence(self):
    ''' expected file structure
        soleares/
        ├── h
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.json
        │   ├── 550d193efe80f67e92d5a0c59ad9d354.svg 
    '''
    paths = glob.glob(f'{self.model}/*/*.json')
    if paths:
      return paths
    else:
      raise FileNotFoundError(f"{self.model}")

  def list_model(self):
    os.chdir(self.workdir)
    return next(os.walk('.'))[1]

  def uniq_cells(self):
    ''' send mondrian the robot a list of uniq cells 
    '''
    seen = dict()
    for row in self.load_model():
      for cell in row:
        seen[cell] = seen[cell] + 1 if cell in seen else 0
    return list(seen.keys())

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
    with open(json_file) as f:
      try:
        conf = json.load(f)
      except:
        print(f"error loading view {json_file}")
        conf = dict()
      init = {}
      for cell in conf:
        init[cell] = dict()
        for a in self.attributes:
          if a in conf[cell]:
            init[cell][a] = conf[cell][a]  # use value from json
          elif a == 'shape_facing' and 'facing' in conf[cell]:
            init[cell][a] = conf[cell]['facing']
          elif a == 'shape_size' and 'size' in conf[cell]:
            init[cell][a] = conf[cell]['size']
          else:
            init[cell][a] = self.attributes[a] # default
    return init

  def load_rinkdata(self, view):
    if view is None:
      raise ValueError("need a digest to make a rink")
    model_data = self.load_model()
    view_data = self.load_view(view)
    if (len(view_data.keys()) != len(self.uniq)):
      raise KeyError(f"missing cells: {view}")
    return {
        'id': self.model,
        'size': (len(model_data[0]), len(model_data)),
        'cells': self.get_cells(model_data, view_data)
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

class Importer:
  ''' based on RINK
  '''
  def add(self, model, db=None):
    ''' load database of named model or use given db'''
    if db is None:
      json_file = f"/tmp/{model}.rink"
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

if __name__ == '__main__':
  i = Importer()
  b = Builder(None)
  db = Db()
  for m in b.list_model():
  #for m in ['buleria']:
    bb = Builder(m)
    for viewpath in bb.find_recurrence(): 
    #for viewpath in ['buleria/m/f11909036a7d7686620546f78ffcf2a9.json']:
      rink = bb.load_rinkdata(viewpath)
      i.add(m, db=rink)
      if m not in db.list_model():
        print(f"adding {m}")
        cells = bb.uniq_cells()
        bs = f'{{{i.blocksize()[0]}, {i.blocksize()[1]}}}'
        if db.set_model(m, len(cells), bs, 1.0):
          for cell in cells:
            for p in i.get_cell(cell)['positions']:
              position = f'{{{p[0]}, {p[1]}}}'
              db.set_blocks(m, position, cell)
      (_, a, filename) = viewpath.split('/')
      author = 'machine' if a == 'm' else 'human'
      view = filename.replace('.json', '')
      if db.count_view(view):
        print(f"skipping view {view}")
      else:
        print(f"adding {view} to {m}")
        db.model = m # self.model was designed to inherit but not the case here
        for cell in bb.uniq_cells():
          items = [cell, m] + list(i.get_cell(cell).values())
          db.write_cell(view, cell, author, items[:13])
