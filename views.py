import random
import psycopg2
from db import Db
from cell import Cell

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
        #output[pos] = cell if top is None else (cell, top)
        output[pos] = (cell, top)
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

  def topcells(self):
    ''' unique list of top cells 
    '''
    self.cursor.execute("""
SELECT distinct(top)
FROM blocks
WHERE top IS NOT null
AND model = %s;""", [self.model])
    rows = self.cursor.fetchall()
    tc = [a[0] for a in rows]
    return tc
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Views(Db):
  ''' a View is a collection of Cells
      valstr = ' '.join(d)
  '''
  def __init__(self):
    self.view = dict() # cell data goes here
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

  def create(self, digest, celldata, model=str, author=str, ver=int, scale=1.0, colournum=0):
    ''' create views metadata and try Cells()
    '''
    try:
      self.cursor.execute("""
INSERT INTO views (view, model, author, scale, colournum)
VALUES (%s, %s, %s, %s, %s);""", [digest, model, author, scale, colournum])
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

  def read(self, digest, celldata=False, output=dict()):
    ''' returns either meta data for a view or cell data 
    '''
    view = None
    if digest and celldata and isinstance(output, list):
      view = self.celldata(digest)
    elif digest and celldata: # convert list to dict
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

  def celldata(self, digest):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink read -v e4681aa9b7aef66efc6290f320b43e55 '''
    data = list()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, p.fill, bg, p.opacity, s.fill, s.width, s.dasharray, s.opacity
FROM cells_new AS c
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

  # TODO this check is for what? Because there is no unique constraint on views table
  # it enforces immutability
  def __count(self, digest):
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

  def generate(self, model=None, ver=1):  # colour45
    rnd = False
    if model is None:
      m = Models()
      model = m.generate()
      # TODO ver = 'universal'
    compass = Compass(model) # compass.conf will be None for unknown models
    b = Blocks(model)
    uniqcells = b.read(output=list())
    topcells = b.topcells()
    c = Cell(ver=ver) 
    for cell in uniqcells:
      topYN = True if cell in topcells else False
      if compass.conf:
        source = 'compass'
        if compass.all(cell):
          c.generate(topYN, facing_all=True)
        else: # this means that cells must have a compass entry
          pair, axis = compass.one(cell)
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
    c = Cells(ver=ver) 
    c.validate(cells)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Cells(Views):
  ''' inherit from View and check that self.pool is mutable in both classes
  '''
  def __init__(self, ver=None):
    self.g = Geometry()
    self.s = Styles()
    self.palette = ver if ver else 'universal'
    self.s.set_spectrum(ver=self.palette)
    self.g.items = { True: list(), False: list() } # stash geoms by top
    self.s.sids = list() # stash styles selected from db
    super().__init__()

  def generate(self, cell, top):
    ''' default is to select from db 
    '''
    if not len(self.g.items[top]):
      self.g.items[top] = self.g.read(top=top)
    self.g.items[top] = self.g.generate(cell, self.g.items[top]) 
    if not len(self.s.sids):
      self.s.sids = self.s.read()
    self.s.sids = self.s.generate(cell, self.s.sids) 

  def generate_any(self, cell, top):
    ''' same as generate except new styles are generated
    '''
    if not len(self.g.items[top]):
      self.g.items[top] = self.g.read(top=top)
    self.g.items[top] = self.g.generate(cell, self.g.items[top]) 
    self.s.generate_any(cell) 

  def generate_one(self, pair, axis, top):
    ''' generate one side of a pair that faces a direction
    '''
    if not len(self.g.items[top]):
      self.g.items[top] = self.g.read(top=top)
    self.g.items[top] = self.g.generate_one(pair, axis, top, self.g.items[top])
    self.s.generate_one(pair, axis)

  def generate_all(self, cell, top):
    ''' facing all directions
    '''
    if not len(self.g.items[top]):
      self.g.items[top] = self.g.read(top=top)
    self.g.items[top] = self.g.generate_all(cell, top, self.g.items[top]) 
    self.s.generate_all(cell) 

  def validate(self, celldata):
    [self.g.validate(c, celldata[c]) for c in celldata]
    [self.s.validate(c, celldata[c]) for c in celldata]

  def create(self, digest, items):
    ''' create a cell by joining a view with geometry and style entries
    '''
    ok = True # used only by unit test
    cell = items.pop(0) # ignore first item cell
    gid = self.g.read(item=items[:4]) 
    if gid is None: # add new geometry
      raise ValueError(f"not expecting to find a new geom {items[:4]}")
      #gid = self.g.create(items=items[:4]) 
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

  # TODO who calls here?
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
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Geometry(Db):
  ''' This class can
      * select existing geometries from a random GID
      * select existing geometries from a given GID
    data is handled as an ordered list (gid, shape, size, facing, top)
  '''
  def __init__(self):
    super().__init__()
    self.attributes = {
      'shape': ['circle', 'line', 'square', 'triangl', 'diamond'],
      'facing': ['all','north', 'south', 'east', 'west'],
      'size': ['medium', 'large'],
      'top': [True, False]
    }
    self.flip = {
      'east': { 'north': 'south', 'south': 'north' },
      'north': { 'west': 'east', 'east': 'west' },
      'northeast': { 'north': 'east', 'east': 'north' },
      'southwest': { 'south': 'west', 'west': 'south' }
    }
    self.defaults = { 'shape':'square', 'size':'medium', 'facing':None, 'top':False }
    self.geom = dict()

  def create(self, items):
    ''' there are finite permutation of geometries so stopped random creation
        also because psycopg2.errors.UniqueViolation # 23505 consumes SERIAL
    '''
    pass

  def read(self, top=None, gid=None, item=list()):
    ''' always returns a list, even if only one member (gid)
    '''
    items = list()
    if gid:  
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
    elif len(item): # in order to commit the item must be converted to a gid
      self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s
AND top = %s;""", item)
      items = self.cursor.fetchone()
    elif isinstance(top, bool):
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE top = %s;""", [top])
      items = self.cursor.fetchall()
    else: # get the lot 
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry;""", [])
      items = self.cursor.fetchall()
    return items

  def generate(self, c, items):
    ''' given a cell and items previously filtered on top randomly select a db entry
    '''
    #print(f"geom {c} items {len(items)}")
    itemsize = len(items) # number of db items to select from
    i = random.choice(range(0, itemsize))
    item = items.pop(i) if itemsize > 1 else items[0]
    z = zip(['shape','size','facing','top'], item) 
    self.geom[c] = dict(z)
    return items

  def generate_all(self, c, top, items):
    ''' if there are more cells than shapes there will be duplicates THATS OK
        to reduce duplication we subtract until only one remains
        there is no random selection because a curated list of geoms avoids weird combinations
        e.g. large diamond
        items with zero ALL entries will throw errors
    '''
    facing_all = [i for i in items if i[2] == 'all'] # i/2 is facing
    poolsize = len(facing_all) # number of db items to select from
    i = random.choice(range(0, poolsize))
    geom = facing_all.pop(i) if poolsize > 1 else facing_all[0]
    self.geom[c] = {
      'shape': geom[0],
      'size': geom[1],
      'facing': 'all',
      'top': top
    }
    return items

  def generate_one(self, pair, axis, top, items):
    ''' use the compass and pair cells along the axis
    '''
    flip = self.flip[axis]
    one = [i for i in items if i[2] in list(flip.keys())] # filter on axis
    i = random.choice(range(0, len(one)))
    geom = one.pop(i) if len(one) > 1 else one[0]
    f = geom[2]
    faces = list([f, flip[f]])
    for i in range(0, 2):
      c = pair[i]
      self.geom[c] = {
        'shape': geom[0],
        'size': geom[1],
        'facing': faces[i], # this makes western line and IT IS FINE
        'top': top
      }
    return items

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
    self.colours = [
      '#FFF','#CCC', '#000', '#F00', '#FF0', '#00F', 
      '#CD5C5C', '#FFA500','#DC143C','#C71585','#4B0082','#32CD32','#9ACD32'
    ]
    self.opacity = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1 ] 
    self.strokes = [n for n in range(0, 11)]
    self.styles = dict()
    self.palette = list()

  def set_spectrum(self, ver=None):
    if ver == 'colour45': # also known as winsor newton 
      #self.spectrum_45()
      backgrounds = ['#FFF', '#9ACD32', '#CD5C5C', '#000']
      foregrounds = ['#C71585', '#DC143C', '#FFA500', '#32CD32', '#4B0082']
      opacity = ["1.0", "0.7", "0.4"]
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
      self.spectrum(backgrounds, foregrounds, opacity, complimentary)
    elif ver == 'htmstarter':
      backgrounds = [ '#FFF', '#000', '#F00', '#00F', '#FF0' ]
      foregrounds = [ '#FFF', '#000', '#F00', '#00F', '#FF0' ]
      opacity = ["1.0"]
      complimentary = {
        '#FFF': '#000', 
        '#000': '#FFF', 
        '#F00': '#FFF', 
        '#FF0': '#00F', 
        '#00F': '#FF0' 
      }
      self.spectrum(backgrounds, foregrounds, opacity, complimentary)
    elif ver == 'universal':
      pass
    else:
      raise ValueError(f"what version are you on about {ver}")

  def spectrum(self, backgrounds, foregrounds, opacity, complimentary):
    ''' organise spectrum in self.palette
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
    for colour in foregrounds:
      fill[colour] = [o for o in opacity]
    for colour in fill:
      for opacity in fill[colour]:
        for bg in backgrounds:
          if colour != bg:
            self.palette.append([colour, opacity, bg])
          # avoid useless permutations (when opacity is 1.0 the background cannot be seen)
          #if opacity == '1.0':
          #  break
    self.fill = fill  # useful for testing validity
    self.backgrounds = backgrounds
    self.complimentary = complimentary

  # TODO if width is 0 then all stroke attributes should be null
  def generate_any(self, c):
    ''' totally rnd no control whatsoever!
    '''
    self.styles[c] = {
      'fill': random.choice(self.colours),
      'bg': random.choice(self.colours),
      'fill_opacity': random.choice(self.opacity),
      'stroke': random.choice(self.colours),
      'stroke_width': random.choice(self.strokes),
      'stroke_dasharray': random.choice(self.strokes),
      'stroke_opacity': random.choice(self.opacity)
    }
    return None

  def generate(self, c, sids):
    #i = random.choice(range(0, len(self.sids)))
    #sid = self.sids.pop(i) if len(self.sids) > 1 else self.sids[0]
    i = random.choice(range(0, len(sids)))
    sid = sids.pop(i) if len(sids) > 1 else sids[0]
    item = self.read(sid)
    z = zip(['fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'], item)
    self.styles[c] = dict(z)
    return sids

  def generate_all(self, cell):
    i = random.choice(range(0, len(self.palette)))
    style = self.palette.pop(i) if len(self.palette) > 1 else self.palette[0]
    #print(f"cell {cell} items {len(self.palette)}")
    fill, opacity, bg = style
    self.styles[cell] = {
      'fill': fill,
      'bg': bg,
      'fill_opacity': opacity,
      'stroke': bg,
      'stroke_width': self.defaults['stroke_width'],
      'stroke_opacity': self.defaults['stroke_opacity'],
      'stroke_dasharray': self.defaults['stroke_dasharray']
    }

  def generate_one(self, pair, axis):
    i = random.choice(range(0, len(self.palette)))
    style = self.palette.pop(i) if len(self.palette) > 1 else self.palette[0]
    fill, opacity, bg = style
    secondary = self.complimentary[fill]
    for i in range(0, 2):
      p = pair[i]
      #print(f"cell {p} items {len(self.palette)}")
      cell = dict()
      cell['bg'] = bg
      cell['fill_opacity'] = opacity
      cell['stroke_dasharray'] = self.defaults['stroke_dasharray']
      cell['stroke_width'] = self.defaults['stroke_width']
      if p: # secondary
        cell['fill'] = secondary
        cell['stroke_opacity'] = self.defaults['stroke_opacity']
        cell['stroke'] = bg
      else: # primary
        cell['fill'] = fill
        cell['stroke_opacity'] = opacity
        cell['stroke'] = fill
      self.styles[p] = cell

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
FROM styles
WHERE stroke_opacity > 0;""", [])
      sids = self.cursor.fetchall()
      return sids

  def validate(self, cell, data):
    # TODO how does this change by version?
    ''' rules for default palette and rules for palette v1 not same
    '''
    if data['stroke'] is None:
      return None
    sw = int(data['stroke_width'])
    #print(sw, self.strokes)
    so = float(data['stroke_opacity'])
    if so not in self.opacity: 
      raise ValueError(f"validation error: opacity {cell}")
    if sw < min(self.strokes) or sw > max(self.strokes):
      raise ValueError(f"validation error: stroke width >{cell}<")
    if data['stroke'] not in self.colours:
      raise ValueError(f"validation error: stroke >{cell}<")
    if self.palette: # palette indicates that spectrum was set to winsor newton
      if data['fill'] not in self.fill: 
        raise ValueError(f"validation error: fill {cell}")
      if data['bg'] not in self.backgrounds: 
        raise ValueError(f"validation error: background >{cell}<")
    else:
      #print(self.colours)
      if data['fill'] not in self.colours: 
        raise ValueError(f"validation error: fill >{cell}<")
      # TODO check bg in Palette not stroke
      if data['bg'] not in self.colours: 
        raise ValueError(f"validation error: background >{cell}<")
    return None
  '''
  the
  end
  '''