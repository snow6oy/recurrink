import random
import psycopg2
from model import Db, ModelData
from cell import CellData
#from model.db import Db
#from model.data import ModelData

class Views(Db):
  ''' a View is an instance of a model, composed from a collection of blocks 
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
    c = CellData(ver=ver)
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

  def readCelldata(self, digest):
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
      view = self.readCelldata(digest)
    else: # convert list to dict
      view = dict()
      data = self.readCelldata(digest)
      for cellvals in data:
        z = zip(self.header, cellvals)
        d = dict(z)
        cell = d['cell']
        del d['cell']         # bit of a tongue twister that one :-D
        view[cell] = d
    return view

  def readMeta(self, digest):
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
    m = ModelData()
    model = m.generate() if model is None else model
    b = BlockData(model)
    #ver = ver if ver else random.choice(range(1, 6)) 
    compass = Compass(model) # compass.conf will be None for unknown models
    uniqcells = b.readPositions(model, output=list())
    topcells = b.topcells(model)
    c = CellData(ver=ver) 
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
    c = CellData(ver=ver) 
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
class BlockData(Db):
  ''' a Block is a collection of Cells
  '''
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

  def readPositions(self, model, output=dict()):
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
