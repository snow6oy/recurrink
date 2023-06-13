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
###############################################################################
class Models(Db):
  ''' a model is the base template
  '''
  def __init__(self):
    super().__init__()

  def set(self, model, uniqcells, blocksizexy, scale):
    success = True
    try:
      self.cursor.execute("""
INSERT INTO models (model, uniqcells, blocksizexy, scale)
VALUES (%s, %s, %s, %s);""", [model, uniqcells, blocksizexy, scale])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

  def get(self, model=None, output='matrix'):
    if output == 'matrix':
      return self.matrix(model)
    elif output == 'list':
      return self.list()
    elif output == 'stats':
      return self.stats()
    else:
      raise ValueError("models only come in three flavours")

  # load_model
  def matrix(self, model):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
    '''
    self.cursor.execute("""
SELECT blocksizeXY
FROM models
WHERE model = %s;""", [model])
    (bsX, bsY) = self.cursor.fetchone()[0]
    data = [[0 for x in range(bsX)] for y in range(bsY)]
    self.cursor.execute("""
SELECT position, cell 
FROM blocks 
WHERE model = %s;""", [model])
    records = self.cursor.fetchall()
    for r in records:
      x = r[0][1] # x is the inner array
      y = r[0][0]
      data[x][y] = r[1]
    return data

  # list_model
  def list(self):
    self.cursor.execute("""
SELECT model
FROM models;""", )
    records = [m[0] for m in self.cursor.fetchall()]
    return records

  # list_model_with_stats
  def stats(self):
    ''' display uniq cells, blocksize and model names
    '''
    output = f"uniq    x    y model\n" + ('-' * 80) + "\n"
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for m in self.cursor.fetchall():
      output += f"{m[1]:>4} {m[2][0]:>4} {m[2][1]:>4} {m[0]}\n"
    return output
###############################################################################
class Blocks(Db):

  def __init__(self, model):
    self.model = model
    super().__init__()

  def set(self, position, cell):
    success = True
    try:
      self.cursor.execute("""
INSERT INTO blocks (model, position, cell)
VALUES (%s, %s, %s);""", [self.model, position, cell])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

  def cells(self, cell_count=0):
    self.cursor.execute("""
SELECT DISTINCT(cell)
FROM blocks
WHERE model = %s;""", [self.model])
    cells = [c[0] for c in self.cursor.fetchall()]
    #print(f"len cells {len(cells)}")
    if cell_count:
      return (len(cells) != cell_count) # True means there is a mismatch
    else: 
      return cells

  def get(self):
    ''' positions link the model and cell: for example 
        model with a line a, x, x a will be represented as positions[(3,0)] : a
        note that lists from db have to be cast to tuples before hashing in a dict
    '''
    positions = dict()
    self.cursor.execute("""
SELECT cell, position
FROM blocks
WHERE model = %s;""", [self.model])
    rows = self.cursor.fetchall()
    for r in rows:
      (cell, pos) = (r[0], tuple(r[1]))
      positions[pos] = cell
    return positions
###############################################################################
class Geometry(Db):
  ''' TODO review shape functions in Draw() as members of this class
    This class can
      * update an existing geometry
      * randomly create new geometries and create a new GID
      * selecting existing geometries from a random GID
      * selecting existing geometries from a given GID
    data is handled as an ordered list (gid, shape, size, facing, top)
    inputs are validated and default values provided for undefined attribute
  '''
  def __init__(self):
    super().__init__()
    self.defaults = { 'shape':'square', 'size':'medium', 'facing':None, 'top':False }
    self.attributes = {
      'shape': ['circle', 'line', 'square', 'triangle', 'diamond'],
      'facing': ['all','north', 'south', 'east', 'west'],
      'size': ['medium', 'large'],
      'top': [True, False]
    }

  def get(self, items=[], rnd=False, gid=0):
    ''' always returns a list, even if only one member (gid)
    '''
    if gid:  # select entries
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
    elif rnd:  # randomly generate a GID and select entries
      self.cursor.execute("""
SELECT MAX(gid)
FROM geometry;""", [])
      maxgid = self.cursor.fetchone()[0]
      # print(f"gid {maxgid}")
      gids = list()
      [gids.append(i) for i in range(1, maxgid + 1)]
      items = self.get(gid=random.choice(gids))  # recursive recurrink :)
    elif len(items): # attempt to select gid
      self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s;""", items[:3])  # ignore top
      items = self.cursor.fetchone()
    else:
      pass # throw error here?
    return items

  def set(self, items=[]):
    ''' create new geometry or add given values to db
        return a list [gid, shape .. top]
    ''' 
    gid = None
    if items:  # validate and update
      items = self.validate(items)
      gid = self.get(items=items)
      if gid is None:
        gid = self.add(items)
    else:      # randomly create new geometries and a new GID
      items.append(random.choice(self.attributes['shape']))
      items.append(random.choice(self.attributes['size']))
      items.append(random.choice(self.attributes['facing']))
      items.append(random.choice(self.attributes['top']))
      items = self.validate(items)
      gid = self.get(items=items) # did we randomly make a new geometry ?
      if gid is None:
        gid = self.add(items)
    return gid + tuple(items)

  def validate(self, items):
    if items[0] in ['square', 'circle']:
      items[2] = 'all'
    if items[0] in ['triangle', 'diamond'] and items[1] == 'large': 
      items[1] = 'medium' # triangles and diamonds cannot be large
    if items[3] and items[1] != 'large': 
      items[3] = False    # only large shapes can be on top
    # TODO items[2] = None
    # write validation test to understand why list comp fails when there is None value
    items = [self.defaults[a] if items[i] is None else items[i] for i, a in enumerate(items)]
    return items

  def add(self, items):
    ''' before calling this attempt to find an existing record and then insert as fallback
        because psycopg2.errors.UniqueViolation:  # 23505 consumes SERIAL
    '''
    self.cursor.execute("""
INSERT INTO geometry (gid, shape, size, facing, top)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING gid;""", items)
    gid = self.cursor.fetchone()
    return gid[0]

  '''
  def get_positions(self, model_data):
    positions = dict()
    for row_num, row in enumerate(model_data):
      for col_num, col in enumerate(row):
        if col not in positions:
          positions[col] = list()
        coord = (col_num, row_num)
        positions[col].append(coord)

    return positions
  '''

###############################################################################
class Styles(Db):

  def __init__(self):
    super().__init__()
    self.fill = {
      'orange':'#FFA500',
      'crimson':'#DC143C',
      'indianred':'#CD5C5C',
      'mediumvioletred':'#C71585',
      'indigo':'#4B0082',
      'limegreen':'#32CD32',
      'yellowgreen':'#9ACD32',
      'black':'#000',
      'white':'#FFF',
      'gray':'#CCC',
      '#fff':'#FFF',
      '#ccc':'#CCC',
      '#333':'#CCC'
    }
    self.defaults = {
     'fill': '#FFF',
      'bg': '#CCC',
      'fill_opacity':1.0,
      'stroke':'#000',
      'stroke_width': 0,
      'stroke_dasharray': 0,
      'stroke_opacity':1.0
    }
    self.colours = ['#FFF','#CCC','#CD5C5C','#000','#FFA500','#DC143C','#C71585','#4B0082','#32CD32','#9ACD32']
    self.opacity = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1 ] 
    self.strokes = [n for n in range(1, 11)]

  def validate(self, items):
    ''' old bad code has various ways of saying RED BLUE GREEN
    '''
    for f in self.fill:
      items[0] = items[0].replace(f, self.fill[f])
      items[1] = items[1].replace(f, self.fill[f])
      items[3] = items[3].replace(f, self.fill[f])
    return items

  def set(self, items=[], sid=None):
    ''' update with sid or insert or randomly create
        always returns a list
    '''
    if sid:
      #print(len(items),sid)  
      items.append(sid)
      self.cursor.execute("""
UPDATE styles SET
fill=%s, bg=%s, fill_opacity=%s, stroke=%s, stroke_width=%s, stroke_dasharray=%s, stroke_opacity=%s
WHERE sid=%s;""", items)
      sid = tuple([sid])  # repackage for consistency
    elif items:
      sid = self.add(items)
    else: # quick make something up!
      items = []
      items.append(random.choice(self.colours))  # fill
      items.append(random.choice(self.colours))  # bg
      items.append(random.choice(self.opacity))  # fill_opacity
      items.append(random.choice(self.colours))  # stroke
      items.append(random.choice(self.strokes))  # width
      items.append(random.choice(self.strokes))  # dash
      items.append(random.choice(self.opacity))  # stroke_opacity
      sid = self.add(items)  # no check for duplication, testing will spam the styles table :/
    return sid + tuple(items)

  def get(self, view=None, cell=None, rnd=False, sid=None):
    ''' select various items according to incoming params
        always return a list
    '''
    styles = list()
    if sid:
      self.cursor.execute("""
SELECT fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM styles
WHERE sid = %s;""", [sid])
      styles = self.cursor.fetchone()
    elif rnd:
      self.cursor.execute("""
SELECT MAX(sid)
FROM styles;""", [])
      maxsid = self.cursor.fetchone()[0]
      sids = list()
      [sids.append(i) for i in range(1, maxsid + 1)]
      styles = self.get(sid=random.choice(sids))
    elif view and cell:
      self.cursor.execute("""
SELECT sid
FROM cells
WHERE view = %s
AND cell = %s;""", [view, cell])
      styles = self.cursor.fetchone()
    else:
      pass # raise error here?
    return styles

  def add(self, items):
    ''' private method called by self.set()
        returns tuple with single elem
    '''
    items = self.validate(items)
    self.cursor.execute("""
INSERT INTO styles (sid, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
RETURNING sid;""", items)
    sid = self.cursor.fetchone()
    print(f"adding sid {sid}")
    return sid

###############################################################################
# TODO should these be done in r.init or here in Views() ?
    #[self.write_cell(view, c, list(cells[c].values())) for c in cells]
    #view = " ".join(row)

class Views(Db):
  ''' a View is a collection of Cells
      valstr = ' '.join(d)
  '''
  def __init__(self):
    self.c = Cells()
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    ''' different from the similar list in self.load_view
    self.header = [
      'cell','model','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ] '''
    super().__init__()

  def delete(self, digest):
    ''' no error checks, this is gonzo style !
    '''
    self.cursor.execute("""
DELETE FROM cells
WHERE view = %s;""", [digest])
    self.cursor.execute("""
DELETE FROM views
WHERE view = %s;""", [digest])
    return True

  def set(self, model, digest, author, control):
    ''' create views metadata and try Cells()
    '''
    if not self.count(digest):
      self.cursor.execute("""
INSERT INTO views (view, model, author, control)
VALUES (%s, %s, %s, %s);""", [digest, model, author, control])
    return digest

  def get(self, digest=None, output=None, model=None):
    ''' returns either data for an existing view
        or an ID for a new view
    '''
    view = str()
    if model:
      (celldata, cells) = self.csvfile(model)
      ''' hashkey should have a unique value for each model view
      '''
      secret = b'recurrink'
      key = ''.join(celldata)
      digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
      digest = digest_maker.hexdigest()
      return digest, cells
    elif digest and len(digest) == 32 and output == 'celldata':
      return self.celldata(digest)
    elif digest and len(digest) == 32:
      self.cursor.execute("""
SELECT *
FROM views
WHERE view = %s;""", [digest])
      row = self.cursor.fetchone()
      row = row[1:3] if row else list() # only need model and author
      return row
    else:
      raise ValueError(f"not expecting this kinda view '{view}'")
    return view

  def generate(self, model, rnd=False):
    ''' generate a config as cell * values matrix
    '''
    b = Blocks(model)
    init = list()
    for cell in b.cells(): 
      row = list()
      row.append(cell)
      if rnd:
        vals = list(self.c.get(control=False))
      else:
        vals = list(self.c.get())
      init.append(vals)
    return init

  def celldata(self, digest):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink.py -m soleares --output RINK --view e4681aa9b7aef66efc6290f320b43e55 '''
    data = dict()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM cells, styles, geometry
WHERE cells.sid = styles.sid
AND cells.gid = geometry.gid
AND view = %s;""", [digest])
    for cellvals in self.cursor.fetchall():
      z = zip(self.header, cellvals)
      d = dict(z)
      cell = d['cell']
      del d['cell']         # bit of a tongue twister that one :-D
      data[cell] = d
    return data
  ''' sample input 
    #for d in data:
    #  if (cell == d[0]):
    #    break
    #return d
  #def convert_row2cell(self, data):
  def convert_row2cell(self, model, data=[]):
      [[ 'a','soleares','triangle','medium','west','#fff','yellowgreen','1.0','#000','1','0','1.0','False' ]] 
    if not len(data):
      data = self.read_tmp_csvfile(model)
    return data
  '''
  def csvfile(self, model):
    ''' example csv row
        a, soleares, square, medium, north, #fff, #ccc, 1.0, #000, 0, 0, 1.0, Fals] '''
    sortdata = list()
    cells = dict()
    to_hash = str()

    with open(f"/tmp/{model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)

    # cell shape size facing top fill bg fill_opacity stroke stroke_width stroke_dasharray stroke_opacity
    # convert values from string to primitives
    for d in data:
      to_hash += ''.join(d)
      d[4] = (d[4] in ['True', 'true'])
      d[9] = int(d[9])
      d[10] = int(d[10])

    # sort them so that top:true will be rendered last
    sortdata = sorted(data, key=lambda x: x[11])

    for d in sortdata:
      z = zip(self.header, d)
      attrs = dict(z)
      cell = attrs['cell']
      #model = attrs['model']
      # pad missing values with default
      #for a in self.attributes:
      #  attrs[a] = self.attributes[a] if a not in attrs else attrs[a] 
      cells.update({cell: attrs})
    return (to_hash, cells)
  ''' combine model and view data to optimise SVG build process
  def get_cells(self, model_data, json_data):
    positions = self.get_positions(model_data)
    for p in positions:
      json_data[p]['positions'] = positions[p]
    return json_data
  '''
  def count(self, digest):
    vcount = 0
    if len(digest) == 32:
      self.cursor.execute("""
SELECT COUNT(view) as vcount
FROM views
WHERE view = %s;""", [digest])
      vcount = self.cursor.fetchone()[0]
    else:
      raise ValueError(f"not expecting this kinda view '{view}'")
    return vcount
###############################################################################
class Cells(Db):
  ''' a cell data set can be initiated in one of three ways
      1. randomly creating cell attributes
      2. selecting existing shapes/syles from any view by given model
      3. cloning attributes from a given view
    data needs to be synchronised between a CSV file and Postgres
    Cells also need to provide default values for undefined attribute
  '''
  def __init__(self):
    self.g = Geometry()
    self.s = Styles()
    '''
    self.attributes = {
      'shape':'square',
      'size':'medium',
      'facing':'north',
      'fill': '#FFF', 
      'bg': '#CCC',
      'fill_opacity':1.0, 
      'stroke':'#000', 
      'stroke_width': 0, 
      'stroke_dasharray': 0,
      'stroke_opacity':1.0,
      'top':False
    }
    '''
    super().__init__()

  # def get(self, model=None, cell=None, control=True):
  def get(self, control=True):
    ''' varying degress of randomness
        with control will select from existing entries
        no control means that entries are randomly generated
    '''
    if control:  
      # print(self.g.get(rnd=True) + self.s.get(rnd=True))
      return self.g.get(rnd=True) + self.s.get(rnd=True)
    else:
      return self.g.set()[1:] + self.s.set()[1:]

  #def write_cell(self, view, cell, items):
  def set(self, view, cell, items):
    ''' update the members of a view
    '''
    update = False # used only by unit test
    # re-order top print(type(top), top)
    # TODO how much longer is this hack requred???
    top = items.pop()
    items.insert(5, bool(top))
    # ignore first 2 items cell and model
    gid = self.g.set(items=items[2:6])[0]
    sid = self.s.get(view, cell)[0]
    sid = self.s.set(items[6:], sid=sid)[0] # retry in case sid was None
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

###############################################################################
#class Recurrink(Db):
class Recurrink():
  ''' read and write data to postgres
  '''
  def __init__(self, model):
    #super().__init__()
    #self.workdir = '/home/gavin/Pictures/artWork/recurrences' # paths are relative to working dir
    self.v = Views()
    m = Models()
    if model in m.get(output='list'):
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
      #self.uniq = self.uniq_cells()
    elif model:
      raise ValueError(f"unknown {model}")

  def init(self, rnd=False, model=None, digest=None):
    control = 0 if rnd else 5
    model, celldata = v.create(model, control, digest)
    tf.write(model, celldata)
    pass
 
  def update(self, model, scale):
    celldata = tf.read(model)
    svg.write(celldata, scale) 
    pass

  def commit(self, model, scale, control, author):
    celldata = tf.read(model)
    digest = v.set(celldata)
    v.add(digest, scale, control, author)
    pass

  def load_rinkdata(self, digest):
    m = Models()
    v = Views()
    model = v.get(digest, 'SOMEMETADATA')
    b = Blocks(model)
    if digest is None:
      raise ValueError("need a digest to make a rink")
    model_data = m.get(model)
    view_data = v.get(digest, output='celldata')
    cell_count = len(view_data.keys())
    if b.cells(cell_count=cell_count):
      raise ValueError(f"{view} is missing cells: {cell_count} is not correct")
    return {
        'id': self.model,
        'size': (len(model_data[0]), len(model_data)),
        'cells': view_data
        #'cells': c.get_cells(model_data, view_data)
    }

  def load_view_csvfile(self, view=None, random=False):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    c = Cells()
    #csvdata = self.read_tmp_csvfile()
    #(model, cellvalues, jsondata) = c.convert_row2cell(csvdata)
    # (model, cellvalues, jsondata) = c.convert_row2cell(self.model)
    (digest, cells) = v.get(model=self.model)
    #if model != self.model:
    #  raise ValueError(f"collision in /tmp {model} is not {self.model}")
    #if view is None:
    #  view = v.get(celldata=cellvalues)
    # view = self.get_digest(cellvalues)
    author = 'machine' if random else 'human'
    return author, digest, cells

  def write_csvfile(self, rnd=False):
    celldata = self.v.generate(self.model, rnd=False) # hardwired until refactor finished
    with open(f"/tmp/{self.model}.csv", 'w') as f:
      for data in celldata:
        c = [str(d) for d in data]
        line = ' '.join(c)
        print(line, file=f)
    return str()

  def write_tmp_csvfile(self, fn, celldata):
    b = Blocks(self.model)
    cells = b.cells()
    with open(fn, 'w') as f:
      wr = csv.writer(f, quoting=csv.QUOTE_NONE)
      wr.writerow(self.header)
      [wr.writerow(celldata[c]) for c in cells]
    return ' '.join(cells)

  def read_tmp_csvfile(self): 
    ''' TODO is this used since it was copied to Cells()
       a, soleares, square, medium, north, #fff, #ccc, 1.0, #000, 0, 0, 1.0, Fals] '''
    with open(f"/tmp/{self.model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)
    return data

  def write_rinkfile(self, view):
    ''' rink input can be from HUMAN or MACHINE
        output is always same 
    '''
    data = self.load_rinkdata(view)
    fn = f"/tmp/{self.model}.rink"
    with open(fn, "w") as outfile:
      json.dump(data, outfile, indent=2)
    return fn

