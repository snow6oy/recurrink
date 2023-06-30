#!/usr/bin/env python3
''' sudo apt-get install python3-psycopg2 
import csv
import json
import sys
'''
import random
import psycopg2

class Db:

  def __init__(self):
    ''' create connection to postgres
    '''
    connection = psycopg2.connect(dbname='recurrink')
    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    self.cursor = connection.cursor()
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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

  def get(self, model=None, output='entry'):
    if output == 'entry':
      return self.entry(model)
    elif output == 'matrix':
      return self.matrix(model)
    elif output == 'list':
      return self.list()
    elif output == 'stats':
      return self.stats()
    else:
      raise ValueError("models only come in three flavours")

  def read(self, model=None):
    ''' fetch a single entry indexed by model 
        return a tuple
    '''
    if model:
      self.cursor.execute("""
SELECT *
FROM models
WHERE model = %s;""", [model])
      entry = self.cursor.fetchone()
      return entry
    else:
      self.cursor.execute("""
SELECT model
FROM models;""", )
      records = [m[0] for m in self.cursor.fetchall()]
      return records

  # load_model
  #def matrix(self, model):
  def positions(self, model):
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
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Blocks(Db):

  def __init__(self, model):
    self.model = model
    super().__init__()

  def create(self, position, cell):
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

  def read(self):
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
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
    super().__init__()

  def delete(self, digest):
    ''' no error checks, this is gonzo style !
        cascade the delete to avoid orphaned styles
    '''
    self.cursor.execute("""
SELECT min(sid), max(sid) 
FROM cells where view = %s;""", [digest])
    minmax = self.cursor.fetchone()
    #print(f"minmax {[minmax]}")
    self.cursor.execute("""
DELETE FROM cells
WHERE view = %s;""", [digest])
    self.cursor.execute("""
DELETE from styles
WHERE sid >= %s and sid <= %s;""", minmax)
    self.cursor.execute("""
DELETE FROM views
WHERE view = %s;""", [digest])
    return True

  # TODO create!
  def create(self, model, digest, author, control=0):
    ''' create views metadata and try Cells()
    '''
    if not self.count(digest):
      self.cursor.execute("""
INSERT INTO views (view, model, author, control)
VALUES (%s, %s, %s, %s);""", [digest, model, author, control])
    return digest

  def read(self, digest, celldata=False, output=dict()):
    ''' returns either meta data for a view or cell data 
    '''
    view = None
    if digest and celldata and isinstance(output, list):
      view = self.celldata(digest)
    elif digest and celldata:
      view = dict()
      data = self.celldata(digest)
      for cellvals in data:
        z = zip(self.header, cellvals)
        d = dict(z)
        cell = d['cell']
        del d['cell']         # bit of a tongue twister that one :-D
        view[cell] = d
    elif digest:
      self.cursor.execute("""
SELECT *
FROM views
WHERE view = %s;""", [digest])
      row = self.cursor.fetchone()
      view = row[1:3] if row else list() # only need model and author
    else:
      raise ValueError(f"not expecting this kinda digest '{digest}'")
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
        vals = list(self.c.generate(1))
      else:
        vals = list(self.c.generate(0))
      init.append(vals)
    return init

  def celldata(self, digest):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink.py -m soleares --output RINK --view e4681aa9b7aef66efc6290f320b43e55 '''
    data = list()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM cells, styles, geometry
WHERE cells.sid = styles.sid
AND cells.gid = geometry.gid
AND view = %s;""", [digest])
    data = self.cursor.fetchall()
    return data

  def count(self, digest):
    vcount = 0
    if len(digest) == 32:
      self.cursor.execute("""
SELECT COUNT(view) as vcount
FROM views
WHERE view = %s;""", [digest])
      vcount = self.cursor.fetchone()[0]
    else:
      raise ValueError(f"not expecting this kinda view '{digest}'")
    return vcount
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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

  def create(self, items):
    ''' each view has its own style
    '''
    items = self.validate(items)
    self.cursor.execute("""
INSERT INTO styles (sid, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
RETURNING sid;""", items)
    sid = self.cursor.fetchone()
    return sid

  def read(self, sid=None):
    if sid:
      styles = list()
      self.cursor.execute("""
SELECT fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM styles
WHERE sid = %s;""", [sid])
      styles = self.cursor.fetchone()
      return styles
    else: # for example output=int() 
      self.cursor.execute("""
SELECT sid
FROM styles;""", [])
      sids = self.cursor.fetchall()
      return sids

  def update(self, sid, items):
    ''' perform crud and returns None as success 
    '''
    items.append(sid) # sql conditional logic needs sid as the last item
    self.cursor.execute("""
UPDATE styles SET
fill=%s, bg=%s, fill_opacity=%s, stroke=%s, stroke_width=%s, stroke_dasharray=%s, stroke_opacity=%s
WHERE sid=%s;""", items)

  def transform(self, control, cells):
    if control == 1:
      for c in cells:
        cells[c]['stroke_width'] = 0
    return cells

  def generate(self, control):
    ''' generate and return a list of 7 values without SID
    '''
    items = []
    if control == 1:
      items.append(random.choice(self.colours))  # fill
      items.append(random.choice(self.colours))  # bg
      items.append(random.choice(self.opacity))  # fill_opacity
      items.append(random.choice(self.colours))  # stroke
      items.append(random.choice(self.strokes))  # width
      items.append(random.choice(self.strokes))  # dash
      items.append(random.choice(self.opacity))  # stroke_opacity
    else: # control 0 is default
      sids = self.read()
      items = self.read(sid=random.choice(sids))
    return items

  def validate(self, items):
    ''' old bad code has various ways of saying RED BLUE GREEN
        called by create and update
    '''
    if len(items) <= 4:
      raise IndexError(f"not enough items {len(items)}")
    for f in self.fill:
      items[0] = items[0].replace(f, self.fill[f])
      items[1] = items[1].replace(f, self.fill[f])
      items[3] = items[3].replace(f, self.fill[f])
    return items
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Cells(Db):
  ''' a cell data set can be initiated in one of three ways
      1. randomly creating cell attributes
      2. selecting existing shapes/syles from any view by given model
      3. cloning attributes from a given view
  '''
  def __init__(self):
    self.g = Geometry()
    self.s = Styles()
    super().__init__()

  def create(self, digest, items):
    ''' create a cell by joining a view with geometry and style entries
    '''
    ok = True # used only by unit test
    cell = items.pop(0)
    gid = self.g.create(items=items[:4]) # ignore first item cell
    sid = self.read(digest, cell)
    if sid is None: # add new style
      sid = self.s.create(items[4:])[0] 
    try:
      self.cursor.execute("""
INSERT INTO cells (view, cell, sid, gid)
VALUES (%s, %s, %s, %s);""", [digest, cell, sid, gid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      ok = False
    return ok

  def read(self, digest, cell):
    ''' return tuple or none
    '''
    self.cursor.execute("""
SELECT sid
FROM cells
WHERE view = %s
AND cell = %s;""", [digest, cell])
    sid = self.cursor.fetchone()
    return sid

  def generate(self, control):
    ''' varying degress of randomness
        with control will select from existing entries
        no control means that entries are randomly generated
        return a tuple(shape .. top)
    '''
    if control == 1:
      #return self.g.set()[1:] + self.s.set()[1:]
      return self.g.generate(control) + self.s.generate(control)
    else:
      # return self.g.get(rnd=True) + self.s.generate(control)
      return self.g.generate(control) + self.s.generate(control)

  def transform(self, control, cells):
    cells = self.g.transform(control, cells)
    return self.s.transform(control, cells)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Geometry(Db):
  '''
    This class can
      * update an existing geometry
      * randomly create new geometries and create a new GID
      * selecting existing geometries from a random GID
      * selecting existing geometries from a given GID
    data is handled as an ordered list (gid, shape, size, facing, top)
    inputs are validated before create or update
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

  def create(self, items):
    ''' before calling this attempt to find an existing record and then insert as fallback
        because psycopg2.errors.UniqueViolation:  # 23505 consumes SERIAL
    '''
    items = self.validate(items)
    gid = self.read(items=items)
    if gid is None:
      self.cursor.execute("""
INSERT INTO geometry (gid, shape, size, facing, top)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING gid;""", items)
      gid = self.cursor.fetchone()
    return gid[0]

  def read(self, items=[], gid=None):
    ''' always returns a list, even if only one member (gid)
    '''
    if gid:  # select entries
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
      return items
    elif len(items): # attempt to select gid
      self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s;""", items[:3])  # ignore top
      gid = self.cursor.fetchone()
      return gid
    else: # provide max to randomly generate a GID
      self.cursor.execute("""
SELECT MAX(gid)
FROM geometry;""", [])
      maxgid = self.cursor.fetchone()[0]
      return maxgid

  def generate(self, control):
    items = list()
    if control == 1: # randomly create new geometries and a new GID
      items.append(random.choice(self.attributes['shape']))
      items.append(random.choice(self.attributes['size']))
      items.append(random.choice(self.attributes['facing']))
      items.append(random.choice(self.attributes['top']))
      items = self.validate(items)
      gid = self.read(items=items) # did we randomly make a new geometry ?
      if gid is None:
        gid = self.create(items)
    else: # assume the postgres SERIAL ensures there are no gaps 
      maxgid = self.read()
      gids = list()
      [gids.append(i) for i in range(1, maxgid + 1)]
      items = self.read(gid=random.choice(gids))  # recursive recurrink :)
    return items 

  def transform(self, control, cells):
    if control == 1:
      for c in cells:
        cells[c]['shape'] = 'square' 
    return cells

  def validate(self, items):
    if items[0] in ['square', 'circle']:
      items[2] = 'all'
    elif items[2] == 'all': 
      items[2] = 'north'
    if items[0] in ['triangle', 'diamond'] and items[1] == 'large': 
      items[1] = 'medium' # triangles and diamonds cannot be large
    if items[3] and items[1] != 'large': 
      items[3] = False    # only large shapes can be on top
    # TODO items[2] = None
    # write validation test to understand why list comp fails when there is None value
    items = [self.defaults[a] if items[i] is None else items[i] for i, a in enumerate(items)]
    return items
