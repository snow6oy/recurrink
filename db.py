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
      models with recipes have top, except koto, pitch and fourfour
      models with top have recipes, except spiral
  '''
  def __init__(self, model):
    conf = {
      'syncopated': {
        'all': ['i', 'j'],
        'north': [('a', 'b'), ('g', 'h'), ('c', 'd'), ('e', 'f')]
        # 'east_NOT': [('a', 'c'), ('g', 'h'), ('b', 'd'), ('e', 'f')],
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
      },
      'koto': {
        'all': ['e', 'f', 'g'],
        'northeast': [ ('b', 'c') ],
        'southwest': [ ('a', 'd') ]
      },
      'pitch': {
        'all': ['b', 'e', 'h'],
        'north': [('c', 'd'), ('j', 'g')],
        'east': [('a', 'f')]
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
    flip = {
      'east': { 'north': 'south', 'south': 'north' },
      'north': { 'west': 'east', 'east': 'west' },
      'northeast': { 'north': 'east', 'east': 'north' },
      'southwest': { 'south': 'west', 'west': 'south' }
    }
    if axis not in flip:
      raise ValueError(f"unknown axis {axis}")
    if self.conf and axis in self.conf:
      return self.conf[axis], flip[axis]
    else:
      return list(), dict()
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
    # TODO is this needed?
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
    # TODO is uniq still needed, see Cells.generate()
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

  def generate(self, model=None):
    rnd = False
    if model is None:
      model = self.m.generate()
      rnd = True
    recipe = self.m.recipe(model) # recipe.conf will be None for unknown models
    b = Blocks(model)
    topcells = b.get_topcells()
    celldata, mesg = self.c.generate(recipe, rnd=rnd, topcells=topcells)
    return model, mesg, celldata

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
  ''' celldata is an aggregation of Geometry and Styles
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

  def generate(self, recipe, rnd=False, topcells=dict()):
    ''' inputs recipe=Recipe(), top=True, 
      topcells={ 'b': None, 'c': 'a', 'b': 'a', 'd': None, 'a': 'c', 'a': 'c' }
    '''
    #print(topcells)
    if recipe.conf:
      self.s.set_spectrum(ver='colour45')
      src = 'recipe'
    else:
      self.s.set_spectrum(ver='universal')
      src = 'random' if rnd else 'database'
    for axis in recipe.axis():  # without recipe.conf being set this will be a null loop
      if axis == 'all':
        self.g.facing_all(recipe.all())
        self.s.facing_all(recipe.all())
      else:
        pairs, flip = recipe.one(axis)
        self.g.facing_one(pairs, flip)
        self.s.facing_one(pairs, flip)
    for c in topcells: # generate data for models without recipe OR cells not defined in recipe
      #print(c, self.g.geom[c]['shape'], self.g.geom[c]['facing'])
      top = topcells[c] # models vary but we cannot risk orphaning top.values
      if c not in self.g.geom: # arbitary test, could be styles
        self.g.generate(c, rnd) 
        self.s.generate(c, rnd)
      if top and top not in self.g.geom: 
        self.g.generate(top, rnd, top=True) 
        self.s.generate(top, rnd)
    celldata = dict()
    for c in self.g.geom: # now that all cells and topcells have vals we ..
      self.g.geom[c]['top'] = True if c in topcells else False
      for a in ['stroke_width', 'stroke_dasharray']:
        self.s.styles[c][a] = self.s.defaults[a] 
      celldata[c] = self.g.geom[c] | self.s.styles[c] # .. finally merge
    return celldata, src

  ''' apply optional symmetry and palette recipes before writing TmpFile
  def transform(self, cells, recipe):
    cells = self.g.transform(cells, recipe)
    return cells
    #TODO return self.s.transform(cells, recipe)
  '''

  def validate(self, celldata, recipe=None):
    # TODO extract a version from recipe and update Styles
    [self.g.validate(c, celldata[c]) for c in celldata]
    [self.s.validate(c, celldata[c]) for c in celldata]
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
    self.geom = dict()

  def create(self, items):
    ''' before calling this attempt to find an existing record and then insert as fallback
        because psycopg2.errors.UniqueViolation:  # 23505 consumes SERIAL
    '''
    #items = self.validate(items)
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
AND top = %s;""", geom)
      gid = self.cursor.fetchone()
      return gid
    else: # get the lot 
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry;""", [])
      items = self.cursor.fetchall()
    return items

  def generate(self, c, rnd, top=False):
    ''' top should not be random. It is set in Cells() for superimposed cells from Blocks()
    '''
    if rnd: # randomly create new geometries and a new GID
      self.geom[c] = dict()
      shape = random.choice(self.attributes['shape'])
      size = random.choice(self.attributes['size'])
      facing = random.choice(self.attributes['facing'])
      if shape == 'triangl' or shape == 'diamond':
        size = 'medium' # triangles and diamonds cannot be large
      if shape in ['square', 'circle']:
        facing = 'all'
      elif shape == 'line' and facing == 'south':
        facing = 'north'
      elif facing == 'line' and facing == 'west':
        facing = 'east'
      elif shape != 'diamond' and facing == 'all': 
        facing = 'north'
      # TODO this check ignore top
      gid = self.read(geom=[shape, size, facing, top]) 
      self.geom[c]['shape'] = shape
      self.geom[c]['size'] = size
      self.geom[c]['facing'] = facing
      self.geom[c]['top'] = top # top is generated here but should be overwritten by Block() later
      if gid is None: # did we randomly make a new geometry ?
        raise ValueError(f"found new geom {self.geom[c]}")
        #gid = self.create(items) 
    else: # without random then a model was given during init, in this case we use pre-defined gids
      all_items = self.read()
      items = random.choice(all_items)
      z = zip(['shape','size','facing','top'], items) # TODO top is overwritten in Cells() so drop it here
      self.geom[c] = dict(z)
    return None

  def facing_all(self, cells):
    ''' select distinct(shape) from geometry where facing = 'all';
        if there are more cells than shapes there will be duplicates THATS OK
        to reduce duplication we subtract until only one remains
        the random selection uses curated list of geoms to avoid weird combinations
        e.g. large diamond
    '''
    items = self.read()
    facing_all = [i for i in items if i[2] == 'all']
    for c in cells:
      i = random.choice(range(0, len(facing_all)))
      geom = facing_all.pop(i) if len(facing_all) > 1 else facing_all[0]
      self.geom[c] = dict()
      self.geom[c]['shape'] = geom[0]
      self.geom[c]['size'] = geom[1]
      self.geom[c]['facing'] = 'all'

  def facing_one(self, pairs, flip):
    ''' use the recipe and pair cells along the axis
    '''
    items = self.read()
    one = [i for i in items if i[2] in list(flip.keys())] # filter on axis

    for p in pairs:
      i = random.choice(range(0, len(one)))
      geom = one.pop(i) if len(one) > 1 else one[0]
      f = geom[2]
      faces = list([f, flip[f]])
      for i in range(0, 2):
        c = p[i]
        self.geom[c] = dict()
        self.geom[c]['shape'] = geom[0]
        self.geom[c]['size'] = geom[1]
        self.geom[c]['facing'] = faces[i] # this makes western line and IT IS FINE

  def validate(self, cell, data):
    if data['shape'] in ['square', 'circle'] and data['facing'] != 'all':
      raise ValueError(f"validation error: circle and square must face all {cell}")
    if data['shape'] in ['triangl', 'line'] and data['facing'] == 'all': 
      raise ValueError(f"validation error: triangles and lines cannot face all {cell}")
    if data['shape'] in ['triangl', 'diamond'] and data['size'] == 'large': 
      raise ValueError(f"validation error: triangle or diamond wrong size {cell}")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Styles(Db):

  def __init__(self):
    super().__init__()
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
    self.strokes = [n for n in range(0, 11)]
    self.styles = dict()
    self.palette = list()

  def set_spectrum(self, ver=None):
    # TODO winsor newton is a better name?
    # and what does UNIVERSAL mean
    if ver == 'colour45':
      self.spectrum_45()
  
  def spectrum_45(self):
    ''' 
    fill: {
      ffa500: [0.4 0.7 1.0]
      32cd32: [0.4 0.7 1.0]
    }
    stroke: {
      ffa500: [0.4 0.7 1.0]
    }
    background: [ FFF, 000, CCC ]
    '''
    fill = dict()
    backgrounds = ['#FFF', '#9ACD32', '#CD5C5C', '#000']
    for colour in ['#C71585', '#DC143C', '#FFA500', '#32CD32', '#4B0082']:
      fill[colour] = [opacity for opacity in ["1.0", "0.7", "0.4"]]
    for colour in fill:
      for opacity in fill[colour]:
        for bg in backgrounds:
          self.palette.append([colour, opacity, bg])
          # avoid useless permutations (when opacity is 1.0 the background cannot be seen)
          if opacity == '1.0':
            break
    self.fill = fill  # useful for testing validity
    self.backgrounds = backgrounds
    return None

  def table(self):
    ''' make document source for palette.pdf
    '''
    xid = 0
    for p in self.palette:
      xid += 1
      print(f'{xid:02} fill: {p[0]} opacity: {p[1]} bg: {p[2]}')

  def generate(self, c, rnd):
    if rnd: # no control whatsoever!
      cell = dict()
      cell['fill'] = random.choice(self.colours)
      cell['bg'] = random.choice(self.colours)
      cell['fill_opacity'] = random.choice(self.opacity)
      cell['stroke'] = random.choice(self.colours)
      cell['stroke_width'] = random.choice(self.strokes)
      if cell['stroke_width'] == 0:
        pass # TODO if width is 0 then all stroke attributes should be null
      else:
        cell['stroke_dasharray'] = random.choice(self.strokes)
        cell['stroke_opacity'] = random.choice(self.opacity)
      self.styles[c] = cell
    else:
      sids = self.read()
      items = self.read(sid=random.choice(sids))
      z = zip(['fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'], items)
      self.styles[c] = dict(z)
    return None

  def facing_all(self, recipe):
    i = random.choice(range(0, len(self.palette)))
    style = self.palette.pop(i) if len(self.palette) > 1 else self.palette[0]
    fill, opacity, bg = style
    for c in recipe:
      cell = dict()
      cell['fill'] = fill
      cell['fill_opacity'] = opacity
      cell['bg'] = bg
      cell['stroke'] = bg
      cell['stroke_opacity'] = '1.0'
      self.styles[c] = cell
      '''
      clone the cell style so top is aligned
      works for overlapping shapes, but not embedded because they disappear!
      top = self.topcells[c]
      if top and c in cells:
        self.styles[top] = cell
      cells.remove(c)
      '''

  def facing_one(self, pairs, axis):
    i = random.choice(range(0, len(self.palette)))
    style = self.palette.pop(i) if len(self.palette) > 1 else self.palette[0]
    fill, opacity, bg = style
    # TODO move this to self.palette and trigger with set_spectrum
    ''' complimentary is not exact to colour theory!
        the exact compliment is commented
    '''
    complimentary = {
      '#DC143C': '#32CD32',  #14dcb4
      '#C71585': '#4B0082',  #15c756
      '#FFA500': '#DC143C',  #005aff
      '#32CD32': '#C71585',  #cd32cd
      '#4B0082': '#FFA500'   #378200
    }
    secondary = complimentary[fill]
    for p in pairs:
      p1 = p[0]
      p2 = p[1]
      cell = dict()
      # TODO refactor as 2 step loop
      # primary
      cell['bg'] = bg
      cell['fill'] = fill
      cell['fill_opacity'] = opacity
      cell['stroke'] = fill
      cell['stroke_opacity'] = opacity
      self.styles[p1] = cell
      # secondary
      cell['bg'] = bg
      cell['fill'] = secondary
      cell['fill_opacity'] = opacity
      cell['stroke'] = bg
      cell['stroke_opacity'] = '1.0'
      self.styles[p2] = cell

  def colour_counter(self):
    # TODO move this to Cells
    ''' colour counter depends on shape
    '''
    seen = dict()
    keys = list()
    for c in self.cells:
      g =self.celldata[c]['geom']
      s =self.celldata[c]['style']
      fo = float(s['fill_opacity'])
      if g['shape'] == 'square' and fo >= 1:
        keys.append(s['fill'])
      else:
        keys.append(s['fill'] + s['fill_opacity'] + s['bg'])
        keys.append(s['bg'])
      if g['stroke_width']:
        keys.append(s['stroke'])

    for k in keys:
      if k in seen:
        seen[k] += 1 
      else:
        seen[k] = 1
    #pp.pprint(seen)
    return(len(seen.keys()))

  def create(self, items):
    ''' each view has its own style
    '''
    # items = self.validate(items)
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

  def validate(self, cell, data):
    # TODO how does this change by version?
    ''' rules for default palette and rules for palette v1 not same
    '''
    sw = int(data['stroke_width'])
    #print(sw, self.strokes)
    so = float(data['stroke_opacity'])
    if so not in self.opacity: 
      raise ValueError(f"validation error: opacity {cell}")
    if sw < min(self.strokes) or sw > max(self.strokes):
      raise ValueError(f"validation error: stroke width {cell}")
    if data['stroke'] not in self.colours:
      raise ValueError(f"validation error: stroke {cell}")
    if self.palette: # palette indicates that spectrum was set to winsor newton
      if data['fill'] not in self.fill: 
        raise ValueError(f"validation error: fill {cell}")
      if data['bg'] not in self.backgrounds: 
        raise ValueError(f"validation error: background {cell}")
    else:
      #print(self.colours)
      if data['fill'] not in self.colours: 
        raise ValueError(f"validation error: fill {cell}")
      if data['bg'] not in self.colours: 
        raise ValueError(f"validation error: background {cell}")
    return None
  '''
  the
  end
  '''
