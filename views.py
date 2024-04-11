import random
import psycopg2
from db import Db
from cell import Cell

class Views(Db):
  ''' a View is a collection of Cells
  '''
  def __init__(self):
    self.view = dict() # cell data goes here
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    super().__init__()

  def update(self, digest):
    ''' capture when view was released to instagram
    '''
    self.cursor.execute("""
UPDATE views SET pubdate=CURRENT_DATE WHERE view = %s;""", [digest])

  def delete(self, digest):
    ''' no error checks, this is gonzo style !
        cascade the delete to cells
    '''
    self.cursor.execute("""
DELETE FROM cells
WHERE view = %s;""", [digest])
    self.cursor.execute("""
DELETE FROM views
WHERE view = %s;""", [digest])
    return True

  def create(self, digest, celldata, model=str, author=str, ver=int, scale=1.0, colournum=0):
    ''' create views metadata and try Cells()
    '''
    try:
      self.cursor.execute("""
INSERT INTO views (view, model, author, scale, colournum, ver)
VALUES (%s, %s, %s, %s, %s, %s);""", [digest, model, author, scale, colournum, ver])
    except psycopg2.errors.UniqueViolation:  # 23505 
      print(f"WARNING {model} {digest} already exists")
    c = Cell(ver=ver)
    [c.create(digest, row) for row in celldata]
    return digest

  def colournum(self, digest=None, count=0):
    if digest and count:
      pass
    else:
      data = dict()
      self.cursor.execute("""
SELECT view, colournum
FROM views;""", [])
      for row in self.cursor.fetchall():
        view, colournum = row
        data[view] = colournum
      return data

  def read_celldata(self, digest):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
          ./recurrink read -v e4681aa9b7aef66efc6290f320b43e55
    '''
    data = list()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, p.fill, bg, p.opacity, s.fill, s.width, s.dasharray, s.opacity
FROM cells AS c
JOIN geometry AS g ON c.gid = g.gid
JOIN palette AS p ON c.pid = p.pid
LEFT JOIN strokes AS s ON c.sid = s.sid
WHERE view = %s
ORDER BY cell;""", [digest])
    for row in self.cursor.fetchall():
      if row[8]: # cell has stroke
        data.append(list(row))
      else:
        data.append(list(row[:8]))
    return data

  def read(self, digest, output=dict()):
    ''' returns a view as cell data in either list or dictionary format
    '''
    view = None
    if isinstance(output, list):
      view = self.read_celldata(digest)
    else: # convert list to dict
      view = dict()
      data = self.read_celldata(digest)
      for cellvals in data:
        z = zip(self.header, cellvals)
        d = dict(z)
        cell = d['cell']
        del d['cell']         # bit of a tongue twister that one :-D
        view[cell] = d
    return view

  def read_meta(self, digest):
    ''' returns meta data for a view
    '''
    meta = list()
    if digest:
      self.cursor.execute("""
SELECT model, author, scale, ver
FROM views
WHERE view = %s;""", [digest])
      row = self.cursor.fetchone()
      meta = row if row else list() # return model author scale
    else:
      raise ValueError(f"not expecting this kinda digest '{digest}'")
    return meta

  #def generate(self, model=None, ver=0): 
  def generate(self, ver, model=None): 
    m = Models()
    model = m.generate() if model is None else model
    #ver = ver if ver else random.choice(range(1, 6)) 
    compass = Compass(model) # compass.conf will be None for unknown models
    uniqcells = m.read_positions(model, output=list())
    topcells = m.topcells(model)
    c = Cell(ver=ver) 
    for cell in uniqcells:
      topYN = True if cell in topcells else False
      if compass.conf:
        source = 'compass'
        pair, axis = compass.one(cell)
        if compass.all(cell):
          c.generate(topYN, facing_all=True)
        elif len(pair):
        #else: # this means that cells must have a compass entry
          #pair, axis = compass.one(cell)
          for i in range(2):
            other = pair[i]
            if other in self.view: # already seen
              c.generate(topYN, axis=axis, facing=self.view[other]['facing'])
            else:
              c.generate(topYN, axis=axis)
      else:
        #print(f"model {model} has no direction")
        source = 'database'
        c.generate(topYN)
      self.view[cell] = c.data
    return model, source, self.view

  def validate(self, cells, ver=str):
    ''' expose Cell.validate here and pass thru so recurrink.update can call
    '''
    c = Cell(ver=ver) 
    c.validate(cells)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Compass(Db):
  ''' compass gives direction to models 
  '''
  def __init__(self, model):
    super().__init__()
    conf = dict()
    self.cursor.execute("""
SELECT *
FROM compass
WHERE model = %s;""", [model])
    compass = self.cursor.fetchall()
    if len(compass):
      for r in compass:
        _, cell, pair, facing = r
        if facing not in conf:
          conf[facing] = list()
        if facing == 'all':
          conf[facing].append(cell)
        else:
          conf[facing].append((cell, pair))
      self.conf = conf
    else:
      self.conf = None

  def axis(self):
    return list(self.conf.keys()) if self.conf else list()

  def all(self, cell):
    ''' test if the given cell is in the model and can face all directions
    '''
    return True if self.conf and 'all' in self.conf and cell in self.conf['all'] else False

  def one(self, cell):
    ''' define the cell pairs (tuples) that face each other
    '''
    pair, facing = tuple(), str()
    if self.conf:
      for axis in self.axis():
        if axis == 'all':
          continue
        for p in self.conf[axis]:
          if cell in p:
            pair = p
            facing = axis
    return pair, facing
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Blocks(Db):

  def __init__(self):
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

  def read_positions(self, model, output=dict()):
    ''' positions link the model and cell: for example 
        model with a line a, x, x a will be represented as positions[(3,0)] : a
    '''
    if type(output) is dict:
      self.cursor.execute("""
SELECT cell, top, position
FROM blocks
WHERE model = %s;""", [model])
      rows = self.cursor.fetchall()
      for r in rows:
        (cell, top, pos) = (r[0], r[1], tuple(r[2]))
        #output[pos] = cell if top is None else (cell, top)
        output[pos] = (cell, top)
    else:  # must be a list
      uniq = dict() # temporary dict to guarantee uniqueness across cell and top
      self.cursor.execute("""
SELECT DISTINCT(cell)
FROM blocks
WHERE model = %s;""", [model])
      for cell in self.cursor.fetchall():
        uniq[cell[0]] = 1
      self.cursor.execute("""
SELECT DISTINCT(top)
FROM blocks
WHERE model = %s
AND top IS NOT null;""", [model])
      for top in self.cursor.fetchall():
        uniq[top[0]] = 1
      output = list(uniq.keys())
    return output

  def topcells(self, model):
    ''' unique list of top cells 
    '''
    self.cursor.execute("""
SELECT distinct(top)
FROM blocks
WHERE top IS NOT null
AND model = %s;""", [model])
    rows = self.cursor.fetchall()
    tc = [a[0] for a in rows]
    return tc
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Models(Blocks):
  ''' models give us the base template to draw a rink
  '''
  def __init__(self): 
    super().__init__()

  def create(self, model, uniqcells, blocksizexy, scale):
    ''' only used once during The Great Import from JSON
    '''
    success = True
    try:
      self.cursor.execute("""
INSERT INTO models (model, uniqcells, blocksizexy, scale)
VALUES (%s, %s, %s, %s);""", [model, uniqcells, blocksizexy, scale])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

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
      if entry:
        return entry
      else:
        raise ValueError(f"nothing found for {model}")
    else:
      self.cursor.execute("""
SELECT model
FROM models;""", )
      records = [m[0] for m in self.cursor.fetchall()]
      return records

  # TODO strip testcard out of the list
  def generate(self):
    models = self.read()
    return random.choice(models)

  def positions(self, model):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
      represented as a string
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
    stats = dict()
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for row in self.cursor.fetchall():
      model, uniq, size = row
      stats[model] = list()
      stats[model].append(uniq)
      stats[model].append(size)
    self.cursor.execute("""
SELECT model, count(top) 
FROM blocks
GROUP BY model;""",)
    top = self.cursor.fetchall()
    model = 'soleares'
    self.cursor.execute("""
SELECT model, count(cell) 
FROM compass
GROUP BY model;""",)
    compass = self.cursor.fetchall()
    for m in stats:
      n = [t for t in top if t[0] == m]
      stats[m].append(n[0][1]) # assume blocks always have model
      i = [c for c in compass if c[0] == m] # but compass does not, so set a default
      counter = i[0][1] if len(i) else 0
      stats[m].append(counter)
    output = f"uniq\t   x\t   y\t top\tcompass\t model\n" + ('-' * 80) + "\n"
    for m in stats:
      output += f"{stats[m][0]:>4}\t{stats[m][1][0]:>4}\t{stats[m][1][1]:>4}\t{stats[m][2]:>4}\t{stats[m][3]:>4}\t{m}\n"
    return output

  def get_scale(self, model):
    return self.read(model=model)[3]

  '''
  the
  end
  '''
  '''
  def get_topcells(self):
    self.cursor.execute("""
SELECT cell, top
FROM blocks
WHERE model = %s;""", [self.model])
    rows = self.cursor.fetchall()
    tc = dict()
    for k, v in rows:
      tc.setdefault(k, v)
    return tc
  '''
