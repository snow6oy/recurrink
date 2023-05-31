#!/usr/bin/env python3
''' sudo apt-get install python3-psycopg2 
'''
import csv
import sys
import json
import hmac
import random
import psycopg2

class Db:

  def __init__(self):
    # Create connection to postgres
    connection = psycopg2.connect(dbname='recurrink')
    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    self.cursor = connection.cursor()

  def load_model(self):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
    '''
    self.cursor.execute("""
SELECT blocksizeXY
FROM models
WHERE model = %s;""", [self.model])
    (bsX, bsY) = self.cursor.fetchone()[0]
    data = [[0 for x in range(bsX)] for y in range(bsY)]
    self.cursor.execute("""
SELECT position, cell 
FROM blocks 
WHERE model = %s;""", [self.model])
    records = self.cursor.fetchall()
    for r in records:
      x = r[0][1] # x is the inner array
      y = r[0][0]
      data[x][y] = r[1]
    return data

  def set_model(self, model, uniqcells, blocksizexy, scale):
    success = True
    try:
      self.cursor.execute("""
INSERT INTO models (model, uniqcells, blocksizexy, scale)
VALUES (%s, %s, %s, %s);""", [model, uniqcells, blocksizexy, scale])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

  def set_blocks(self, model, position, cell):
    success = True
    try:
      self.cursor.execute("""
INSERT INTO blocks (model, position, cell)
VALUES (%s, %s, %s);""", [model, position, cell])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

  def list_model(self):
    self.cursor.execute("""
SELECT model
FROM models;""", )
    records = [m[0] for m in self.cursor.fetchall()]
    return records

  def list_model_with_stats(self):
    ''' display uniq cells, blocksize and model names
    '''
    output = f"uniq    x    y model\n" + ('-' * 80) + "\n"
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for m in self.cursor.fetchall():
      output += f"{m[1]:>4} {m[2][0]:>4} {m[2][1]:>4} {m[0]}\n"
    return output

  def uniq_cells(self):
    self.cursor.execute("""
SELECT DISTINCT(cell)
FROM blocks
WHERE model = %s;""", [self.model])
    cells = [c[0] for c in self.cursor.fetchall()]
    return cells

  def count_view(self, view):
    vcount = 0
    if len(view) == 32:
      self.cursor.execute("""
SELECT COUNT(view) as vcount
FROM views
WHERE view = %s;""", [view])
      vcount = self.cursor.fetchone()[0]
    else:
      raise ValueError(f"not expecting this kinda view '{view}'")
    return vcount

  def load_view(self, view):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink.py -m soleares --output RINK --view e4681aa9b7aef66efc6290f320b43e55 '''
    header = [
      'cell','shape','shape_size','shape_facing','top','fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    data = dict()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM views, styles, geometry
WHERE views.sid = styles.sid
AND views.gid = geometry.gid
AND view = %s;""", [view])
    for cellvals in self.cursor.fetchall():
      z = zip(header, cellvals)
      d = dict(z)
      cell = d['cell']
      del d['cell']         # bit of a tongue twister that one :-D
      data[cell] = d
    return data

  def write_cell(self, view, cell, author, items):
    ''' update a a single row in the views table
    '''
    update = False # used only by unit test
    # re-order top print(type(top), top)
    top = items.pop()
    items.insert(5, bool(top))
    # ignore first 2 items cell and model
    gid = self.set_geometry(items[2:6])
    sid = self.get_style(view, cell)
    sid = self.set_styles(items[6:], sid=sid)
    # UPSERT the view table
    try:
      self.cursor.execute("""
INSERT INTO views (view, cell, model, author, sid, gid)
VALUES (%s, %s, %s, %s, %s, %s);""", [view, cell, self.model, author, sid, gid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      update = True
      self.cursor.execute("""
UPDATE views SET
author=%s, sid=%s, gid=%s
WHERE view=%s
AND cell=%s;""", [author, sid, gid, view, cell])
    return update

  def set_geometry(self, items):
    ''' first attempt to find an existing record and then insert as fallback
    '''
    gid = None

    if items[0] in ['triangle', 'diamond'] and items[1] == 'large': 
      items[1] = 'medium' # triangles and diamonds cannot be large
    if items[3] and items[1] != 'large': 
      items[3] = False    # only large shapes can be on top

    # avoid this psycopg2.errors.UniqueViolation:  # 23505 because it consumes SERIAL
    self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s;""", items[:3])  # ignore top
    gid = self.cursor.fetchone()

    if not gid:
      self.cursor.execute("""
INSERT INTO geometry (gid, shape, size, facing, top)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING gid;""", items)
      gid = self.cursor.fetchone()
    return gid[0]

  def set_styles(self, items, sid=None):
    ''' update with sid or insert otherwise
    '''
    if sid:
      #print(len(items),sid)  
      items.append(sid)
      self.cursor.execute("""
UPDATE styles SET
fill=%s, bg=%s, fill_opacity=%s, stroke=%s, stroke_width=%s, stroke_dasharray=%s, stroke_opacity=%s
WHERE sid=%s;""", items)
    else:
      self.cursor.execute("""
INSERT INTO styles (sid, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
RETURNING sid;""", items)
      sid = self.cursor.fetchone()[0]
    return sid

  def get_style(self, view, cell):
    self.cursor.execute("""
SELECT sid
FROM views
WHERE view = %s
AND cell = %s;""", [view, cell])
    sid = self.cursor.fetchone()
    return sid[0] if sid else None
###############################################################################
class Recurrink(Db):
  ''' read and write data to postgres
  '''
  def __init__(self, model, machine=False):
    super().__init__()
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

  def write_rinkfile(self, view):
    ''' rink input can be from HUMAN or MACHINE
        output is always same 
    '''
    data = self.load_rinkdata(view)
    fn = f"/tmp/{self.model}.rink"
    with open(fn, "w") as outfile:
      json.dump(data, outfile, indent=2)
    return fn

  def write_view(self, view=None, random=False):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")
    if view is None:
      view = self.get_digest(cellvalues)
    author = 'machine' if random else 'human'

    [self.write_cell(view, cell, author, list(jsondata[cell].values())) for cell in jsondata]
    return view

  #####################################################################
  ######################### p r i v a t e #############################

  def write_tmp_csvfile(self, fn, celldata):
    cells = self.uniq
    with open(fn, 'w') as f:
      wr = csv.writer(f, quoting=csv.QUOTE_NONE)
      wr.writerow(self.header)
      [wr.writerow(celldata[c]) for c in cells]
    return ' '.join(cells)

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


  def convert_row2cell(self, data):
    ''' sample input 
      [[ 'a','soleares','triangle','medium','west','#fff','yellowgreen','1.0','#000','1','0','1.0','False' ]] '''
    sortdata = list()
    source = dict()
    to_hash = str()

    # convert values from string to primitives
    for d in data:
      to_hash += ''.join(d)
      d[9] = int(d[9])
      d[10] = int(d[10])
      d[12] = (d[12] in ['True', 'true'])

    # sort them so that top:true will be rendered last
    sortdata = sorted(data, key=lambda x: x[12])

    for d in sortdata:
      z = zip(self.header, d)
      attrs = dict(z)
      cell = attrs['cell']
      model = attrs['model']
      # pad missing values with default
      for a in self.attributes:
        attrs[a] = self.attributes[a] if a not in attrs else attrs[a] 
      source.update({cell: attrs})
    return (model, to_hash, source)

  def get_digest(self, cellvalues):
    ''' hashkey should have a unique value for each model view
    '''
    secret = b'self.model'
    key = ''.join(cellvalues)
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    return digest_maker.hexdigest()

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
    ''' example csv row
       a, soleares, square, medium, north, #fff, #ccc, 1.0, #000, 0, 0, 1.0, Fals] '''
    with open(f"/tmp/{self.model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)
    return data

###############################################################################
###############################################################################

  def _uniq_cells(self):
    ''' send mondrian the robot a list of uniq cells 
    '''
    seen = dict()
    for row in self.load_model():
      for cell in row:
        seen[cell] = seen[cell] + 1 if cell in seen else 0
    return seen.keys()

  def _load_model(self):
    ''' load csv data
    '''
    csvfile = f"{self.model}/index.csv"
    # print("load model " + csvfile)
    with open(csvfile) as f:
      reader = csv.reader(f, delimiter=' ')
      data = list(reader)
    return data

  def _load_view(self, json_file):
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


  def _write_jsonfile(self):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")

    digest = self.get_digest(cellvalues) # if self.author == 'MACHINE' else self.model
    self.write_json(f"/tmp/{self.model}.json", jsondata)
    return digest

  def _find_recurrence(self, file, ext):
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

  def _list_model(self):
    os.chdir(self.workdir)
    return next(os.walk('.'))[1]

  def _list_model_with_stats(self):
    print(f"uniq    x    y model")
    print('-' * 80)
    for m in self.list_model():
      self.model = m
      index_csv = self.load_model()
      (x, y) = (len(index_csv[0]), len(index_csv))
      print(f"{len(self.uniq_cells()):>4} {x:>4} {y:>4} {m}")

  def _write_jsonfile(self, view, author=None):
    ''' convert a 2d array of cell data into a hash and json file
    DEPRECATED see write_view
    '''
    #csvdata = self.read_tmp_csvfile()
    #(model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    update = False
    model = 'soleares'
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")
    jsondata = {
      'a': {
        'shape':'triangle', 
        'size': 'medium', 
        'facing': 'south', 
        'top': True,
        'fill': '#0f0',
        'bg': 'gray'
       }
    }
    # digest = self.get_digest(cellvalues) # if self.author == 'MACHINE' else self.model
    #self.write_json(f"/tmp/{self.model}.json", jsondata)
    for cell in 'a':
      items = list(jsondata[cell].values())
      gid = self.set_geometry(items)
      sid = self.set_styles(items)
      # UPSERT the view table
      try:
        self.cursor.execute("""
INSERT INTO views (view, cell, model, author, sid, gid)
VALUES (%s, %s, %s, %s, %s, %s);""", [view, cell, self.model, author, sid, gid])
      except psycopg2.errors.UniqueViolation:  # 23505 
        update = True
        self.cursor.execute("""
UPDATE views SET
author=%s, sid=%s, gid=%s
WHERE view=%s
AND cell=%s;""", [author, sid, gid, view, cell])
      digest = f"{update} updated"
    return digest
