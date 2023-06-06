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

  def load_view(self, view):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink.py -m soleares --output RINK --view e4681aa9b7aef66efc6290f320b43e55 '''
    header = [
      'cell','shape','size','facing','top','fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    data = dict()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM cells, styles, geometry
WHERE cells.sid = styles.sid
AND cells.gid = geometry.gid
AND view = %s;""", [view])
    for cellvals in self.cursor.fetchall():
      z = zip(header, cellvals)
      d = dict(z)
      cell = d['cell']
      del d['cell']         # bit of a tongue twister that one :-D
      data[cell] = d
    return data

  def write_cell(self, view, cell, items):
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
    # UPSERT the cells
    try:
      self.cursor.execute("""
INSERT INTO cells (view, cell, sid, gid)
VALUES (%s, %s, %s, %s);""", [view, cell, sid, gid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      update = True
      self.cursor.execute("""
UPDATE cells SET
sid=%s, gid=%s
WHERE view=%s
AND cell=%s;""", [sid, gid, view, cell])
    return update

  ''' update a a single row in the views table
  def write_cell(self, view, cell, author, items):
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
  '''

  def set_geometry(self, items):
    ''' first attempt to find an existing record and then insert as fallback
    '''
    gid = None

    if items[0] in ['square', 'circle']:
      items[2] = 'all'
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
    fill = {
      'orange':'#FFA500',
      'crimson':'#DC143C',
      'indianred':'#CD5C5C',
      'mediumvioletred':'#C71585',
      'indigo':'#4B0082',
      '#4B0083':'#4B0082',
      'limegreen':'#32CD32',
      'yellowgreen':'#9ACD32',
      'black':'#000',
      'white':'#FFF',
      'gray':'#CCC',
      '#fff':'#FFF',
      '#ccc':'#CCC',
      '#333':'#CCC'
    }
    for f in fill:
      items[0] = items[0].replace(f, fill[f])
      items[1] = items[1].replace(f, fill[f])
      items[3] = items[3].replace(f, fill[f])

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
FROM cells
WHERE view = %s
AND cell = %s;""", [view, cell])
    sid = self.cursor.fetchone()
    return sid[0] if sid else None
###############################################################################
class Views(Db):

  def __init__(self):
    super().__init__()

  def delete(self, view):
    ''' no error checks, this is gonzo style !
    '''
    self.cursor.execute("""
DELETE FROM cells
WHERE view = %s;""", [view])
    self.cursor.execute("""
DELETE FROM views
WHERE view = %s;""", [view])
    return True

  def set(self, model, view, author, control):
    ''' create views metadata and try Cells()
    '''
    if not self.count(view):
      self.cursor.execute("""
INSERT INTO views (view, model, author, control)
VALUES (%s, %s, %s, %s);""", [view, model, author, control])

    #[self.write_cell(view, c, list(cells[c].values())) for c in cells]
    return view

  def get(self, vid=None, celldata=None):
    ''' returns either data for an existing view
        or an ID for a new view
    '''
    view = str()
    if vid and len(vid) == 32:
      self.cursor.execute("""
SELECT *
FROM views
WHERE view = %s;""", [vid])
      row = self.cursor.fetchone()
      row = row[1:3] if row else list() # only need model and author
      view = " ".join(row)
    elif celldata is not None:
      ''' hashkey should have a unique value for each model view
      '''
      secret = b'recurrink'
      key = ''.join(celldata)
      digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
      view = digest_maker.hexdigest()
    else:
      raise ValueError(f"not expecting this kinda view '{view}'")
    return view

  def count(self, view):
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


###############################################################################
class Recurrink(Db):
  ''' read and write data to postgres
  '''
  def __init__(self, model):
    super().__init__()
    self.workdir = '/home/gavin/Pictures/artWork/recurrences' # paths are relative to working dir
    models = self.list_model() 
    if model in models:
      self.model = model

      self.attributes = {
        'shape':'square',
        'size':'medium',
        'facing':'north',
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
      # self.author = 'MACHINE' if machine else 'HUMAN'
      self.uniq = self.uniq_cells()
    elif model:
      raise ValueError(f"unknown {model}")

  #################################################################
  ################ p u b l i c ####################################

  def write_csvfile(self, rnd=False):
    ''' generate a config as cell x values matrix
        for humans copy default values over
        but machines get randoms
    '''
    init = dict()
    for c in self.uniq: 
      randomvals = self.random_cellvalues(c) if rnd else dict()
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
      raise KeyError(f"missing cells: {view}: {len(view_data.keys())} is not {len(self.uniq)}")
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

  def load_view_csvfile(self, view=None, random=False):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")
    if view is None:
      v = Views()
      view = v.get(celldata=cellvalues)
      # view = self.get_digest(cellvalues)
    author = 'machine' if random else 'human'

    return author, view, jsondata

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
    rnd['shape'] = random.choice(["circle", "line", "square", "triangle", "diamond"])
    rnd['facing'] = random.choice(["north", "south", "east", "west"])
    # default 'shape_size':'medium',
    sizes = ["medium", "large"]
    if rnd['shape'] == "triangle":
      rnd['size'] = "medium"
    else:
      rnd['size'] = random.choice(sizes)
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
