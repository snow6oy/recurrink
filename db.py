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
class Recipe:
  ''' recipes are hardcode here but when better defines will move to Postgres
  '''
  def __init__(self, model):
    conf = {
      'syncopated': {
        'all': ['i', 'j'],
        'east_NOT': [('a', 'c'), ('g', 'h'), ('b', 'd'), ('e', 'f')],
        'north': [('a', 'b'), ('g', 'h'), ('c', 'd'), ('e', 'f')]
      },
      'marchingband': {
        'all': ['e', 'f'],
        'north': [('b', 'c')],
        'east': [('a', 'd')]
      },
      'timpani': {
        'all': ['e', 'f', 'k'],
        'northeast': [ ('a', 'b'), ('c', 'd'), ('g', 'h'), ('i', 'j') ]
      },
      'soleares': {
        'all': ['a', 'c'],
        'east': [('b', 'd')]
      },
      'fourfour': {
        'all': ['a', 'd', 'h', 'a'],
        'northeast': [ ('b', 'c'), ('f', 'g'), ('i', 'k'), ('j', 'l') ]
      }
    }
    self.conf = conf[model] if model in conf else None

  def axis(self):
    return list(self.conf.keys()) if self.conf else list()

  def all(self):
    ''' define the cells in the model that can face any direction
    '''
    return self.conf['all'] if self.conf else list()

  def one(self, axis):
    ''' define the cell pairs (tuples) that face each other
    '''
    if self.conf and axis in self.conf:
      return self.conf[axis] 
    else:
      return list()
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Models(Db):
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
      return entry
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
    output = f"uniq    x    y model\n" + ('-' * 80) + "\n"
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for m in self.cursor.fetchall():
      output += f"{m[1]:>4} {m[2][0]:>4} {m[2][1]:>4} {m[0]}\n"
    return output
 
  def recipe(self, model):
    r = Recipe(model)
    return r
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

  def read(self, output=dict()):
    ''' positions link the model and cell: for example 
        model with a line a, x, x a will be represented as positions[(3,0)] : a
    '''
    if type(output) is dict:
      self.cursor.execute("""
SELECT cell, top, position
FROM blocks
WHERE model = %s;""", [self.model])
      rows = self.cursor.fetchall()
      for r in rows:
        (cell, top, pos) = (r[0], r[1], tuple(r[2]))
        output[pos] = cell if top is None else (cell, top)
    else:  # must be a list
      uniq = dict() # temporary dict to guarantee uniqueness across cell and top
      self.cursor.execute("""
SELECT DISTINCT(cell)
FROM blocks
WHERE model = %s;""", [self.model])
      for cell in self.cursor.fetchall():
        uniq[cell[0]] = 1
      self.cursor.execute("""
SELECT DISTINCT(top)
FROM blocks
WHERE model = %s
AND top IS NOT null;""", [self.model])
      for top in self.cursor.fetchall():
        uniq[top[0]] = 1
      output = list(uniq.keys())
    return output

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Views(Db):
  ''' a View is a collection of Cells
      valstr = ' '.join(d)
  '''
  def __init__(self):
    self.m = Models()
    self.c = Cells()
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    super().__init__()

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

  def create(self, model, digest, author, scale=1.0):
    ''' create views metadata and try Cells()
    '''
    if not self.count(digest):
      self.cursor.execute("""
INSERT INTO views (view, model, author, scale)
VALUES (%s, %s, %s, %s);""", [digest, model, author, scale])
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
      view = row[1:4] if row else list() # return model author scale
    else:
      raise ValueError(f"not expecting this kinda digest '{digest}'")
    return view

  ''' generate a config as cell * values matrix
  def generate(self, model=None):
    rnd=False
    if model is None:
      rnd = True
      model = self.m.generate()
    b = Blocks(model)
    init = list()
    for cell in b.read(output=list()): 
      celldata = [cell]
      if rnd:
        celldata += list(self.c.generate(1))
      else:
        celldata += list(self.c.generate(0))
      init.append(celldata)
    return model, init
  '''

  def generate(self, model=None):
    ''' generate a config as cell * values matrix
    '''
    recipe = None  # replace random with recipe
    rnd = False
    if model is None:
      model = self.m.generate()
      rnd = True
    else: # load recipes for model
      recipe = self.m.recipe(model)
    b = Blocks(model)
    init = dict()
    #  'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    for cell in b.read(output=list()): 
      init[cell] = dict()
      cellrow = self.c.generate(rnd)
      init[cell]['geom'] = dict(zip(self.header[1:5], cellrow[:4]))
      init[cell]['style'] = dict(zip(self.header[5:9], cellrow[4:8]))
      init[cell]['geom']['stroke_width'] = cellrow[8]
      init[cell]['style']['stroke_dasharray'] = cellrow[9]
      init[cell]['style']['stroke_opacity'] = cellrow[10]

    celldata = self.c.transform(init, recipe)
    return model, celldata

  def celldata(self, digest):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink read -v e4681aa9b7aef66efc6290f320b43e55 '''
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
    cell = items.pop(0) # ignore first item cell
    gid = self.g.read(geom=items[:4]) 
    if gid is None: # add new geometry
      gid = self.g.create(items=items[:4]) 
    sid = self.s.read(style=items[4:])
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

  def generate(self, rnd):
    ''' varying degress of randomness
        with control will select from existing entries
        no control means that entries are randomly generated
        return a tuple(shape .. top)
    '''
    return self.g.generate(rnd) + self.s.generate(rnd)

  def transform(self, cells, recipe):
    cells = self.g.transform(cells, recipe)
    return cells
    #TODO return self.s.transform(cells, recipe)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Geometry(Db):
  '''
    This class can
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
      'shape': ['circle', 'line', 'square', 'triangl', 'diamond'],
      'facing': ['all','north', 'south', 'east', 'west'],
      'size': ['medium', 'large'],
      'top': [True, False]
    }

  def create(self, items):
    ''' before calling this attempt to find an existing record and then insert as fallback
        because psycopg2.errors.UniqueViolation:  # 23505 consumes SERIAL
    '''
    items = self.validate(items)
    self.cursor.execute("""
INSERT INTO geometry (gid, shape, size, facing, top)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING gid;""", items)
    gid = self.cursor.fetchone()
    return gid[0]

  def read(self, geom=[], gid=None):
    ''' always returns a list, even if only one member (gid)
    '''
    if gid:  # select entries
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
      return items
    elif len(geom): # attempt to select gid
      self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s
AND top = %s;""", geom)  # items[:3])  # ignore top
      gid = self.cursor.fetchone()
      return gid
    else: # provide max to randomly generate a GID
      self.cursor.execute("""
SELECT gid
FROM geometry;""", [])
      gids = self.cursor.fetchall()
      return gids

  def generate(self, rnd):
    items = list()
    if rnd: # randomly create new geometries and a new GID
      items.append(random.choice(self.attributes['shape']))
      items.append(random.choice(self.attributes['size']))
      items.append(random.choice(self.attributes['facing']))
      items.append(random.choice(self.attributes['top']))
      items = self.validate(items)
      gid = self.read(geom=items) # did we randomly make a new geometry ?
      if gid is None:
        gid = self.create(items) 
    else: # without random then a model was given during init, in this case we use pre-defined gids
      gids = self.read()
      items = self.read(gid=random.choice(gids))
    return items 

  # TODO
  # call validate during generate
  def transform(self, celldata, recipe):
    self.celldata = celldata
    for axis in recipe.axis():
      if axis == 'all':
        self.facing_all(recipe.all())
      else:
        self.facing_one(recipe.one(axis), axis)
    return self.celldata
    '''
    move transform into recipe, soleares square all 
    if control == 1:
      for c in cells:
        cells[c]['shape'] = 'square' 
    elif control == 2:
      for c in cells:
        cells[c]['shape'] = 'diamond' 
    '''

  def facing_all(self, cells):
    ''' select distinct(shape) from geometry where facing = 'all';
        if there are more cells than shapes there will be duplicates
        but to reduce duplication we remove the option until only one remains
    '''
    shape = ['circle', 'diamond', 'square']
    # [print(c) for c in cells]
    for c in cells:
      s = random.choice(shape)
      self.celldata[c]['geom']['shape'] = s
      self.celldata[c]['geom']['facing'] = 'all'
      if len(shape) > 1:
        shape.remove(s)

  def facing_one(self, pairs, axis):
    ''' TODO select distinct(shape) from geometry where facing = 'north';
    '''
    #print(axis)
    #[print(p) for p in pairs]
    shape = ['triangl', 'diamond', 'line']
    if axis == 'east':
      facing = { 'north': 'south', 'south': 'north' }
    elif axis == 'northeast':
      facing = { 'north': 'east', 'east': 'north' }
    else:
      facing = { 'west': 'east', 'east': 'west' }
    for p in pairs:
      s = random.choice(shape)
      f1 = random.choice(list(facing.keys()))
      if s == 'line' and f1 == 'west':  # lines cannot be south or west 
        f1 = f2 = 'east'
      elif s == 'line' and f1 == 'south':  # lines cannot be south or west 
        f1 = f2 = 'north'
      else:
        f2 = facing[f1]
      c1 = p[0]
      c2 = p[1]
      self.celldata[c1]['geom']['shape'] = s
      self.celldata[c1]['geom']['facing'] = f1
      self.celldata[c2]['geom']['shape'] = s
      self.celldata[c2]['geom']['facing'] = f2

  def validate(self, items):
    ''' shape/0 and facing/2 have dependencies
    '''
    if items[0] == 'south':
      items[0] = 'north'
    if items[0] == 'west':
      items[0] = 'east'
    if items[0] in ['square', 'circle']:
      items[2] = 'all'
    elif items[0] != 'diamond' and items[2] == 'all': 
      items[2] = 'north'
    if items[0] in ['triangl', 'diamond'] and items[1] == 'large': 
      items[1] = 'medium' # triangles and diamonds cannot be large
    #if items[3] and items[1] != 'large': 
    #  items[3] = False    # only large shapes can be on top
    # TODO items[2] = None
    # write validation test to understand why list comp fails when there is None value
    items = [self.defaults[a] if items[i] is None else items[i] for i, a in enumerate(items)]
    return items
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Styles(Db):

  def __init__(self):
    super().__init__()
    self.fill = {
      'cyan':'#CD5C5C',
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

  def read(self, sid=None, style=list()):
    if sid:
      styles = list()
      self.cursor.execute("""
SELECT fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM styles
WHERE sid = %s;""", [sid])
      styles = self.cursor.fetchone()
      return styles
    elif style:
      self.cursor.execute("""
SELECT sid
FROM styles
WHERE fill = %s
AND bg = %s
AND fill_opacity = %s
AND stroke = %s
AND stroke_width = %s
AND stroke_dasharray = %s
AND stroke_opacity = %s;""", style)
      sid = self.cursor.fetchone()
      return sid
    else: # for example output=int() 
      self.cursor.execute("""
SELECT sid
FROM styles;""", [])
      sids = self.cursor.fetchall()
      return sids

  '''
  def transform(self, control, cells):
    if control == 1:
      for c in cells:
        cells[c]['stroke_width'] = 0 
    elif control == 2:
      for c in cells:
        cells[c]['stroke_width'] = 1 
    return cells
  '''

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
