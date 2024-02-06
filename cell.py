import random
import psycopg2
from db import Db

class Geometry(Db):
  ''' Generate a geometry by selecting existing geometries from db
      Validate input geometries
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

  def create(self, items):
    ''' there are finite permutation of geometries so stopped random creation
        also because psycopg2.errors.UniqueViolation # 23505 consumes SERIAL
    '''
    pass

  #def read(self, top=None, gid=None, item=list()):
  def read(self, top=None, gid=None):
    ''' always returns a list, even if only one member (gid)
    '''
    items = list()
    if gid:  
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
    elif isinstance(top, bool):
      pass # self.load()
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE top = %s;""", [top])
      items = self.cursor.fetchall()
    return items

  def read_gid(self, item):
    ''' in order to commit the item must be converted to a gid
    '''
    self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s
AND top = %s;""", item)
    gid = self.cursor.fetchone()
    if gid is None: # add new geometry
      raise ValueError(f"not expecting to find a new geom {item}")
    return gid[0]

  def read_one(self, flip):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE facing = %s
OR facing = %s
ORDER BY random() LIMIT 1;""", flip)
    return list(self.cursor.fetchone())

  def read_all(self, top):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE facing = 'all'
AND top = %s
ORDER BY random() LIMIT 1;""", [top])
    return self.cursor.fetchone()

  def read_any(self, top):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE top = %s
ORDER BY random() LIMIT 1;""", [top])
    return list(self.cursor.fetchone())

  def generate_any(self, top=False):
    ''' randomly select a db entry filtered on top
    '''
    return dict(zip(['shape','size','facing','top'], Geometry.read_any(self, top)))

  def generate_all(self, top=False):
    return dict(zip(['shape','size','facing','top'], self.read_all(top)))

  def generate_one(self, axis, top, facing=None):
    ''' use the compass and pair cells along the axis
    '''
    flip = self.flip[axis]
    geom = self.read_one(list(flip.keys()))
    geom[2] = flip[facing] if facing else geom[2] # this makes western line and IT IS FINE
    geom[3] = top
    return dict(zip(['shape','size','facing','top'], geom))

  def validate(self, cell, data):
    #print(f"{cell}\tshape {data['shape']} size {data['size']} facing {data['facing']} top {data['top']}")
    if data['shape'] in ['square', 'circle'] and data['facing'] != 'all':
      raise ValueError(f"validation error: circle and square must face all {cell}")
    if data['shape'] in ['triangl', 'line'] and data['facing'] == 'all': 
      raise ValueError(f"validation error: triangles and lines cannot face all {cell}")
    if data['shape'] in ['triangl', 'diamond'] and data['size'] in ['large', 'small']: 
      raise ValueError(f"validation error: triangle or diamond wrong size {cell}")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Palette(Geometry):

  def __init__(self, ver):
    super().__init__()
    self.ver = ver # universal is set as default by recurrink
    self.opacity = self.read_opacity()
    self.zeroten = [n for n in range(1, 11)]

  def create(self, items):
    ''' for palette creation see celldata.py
    '''
    pass

  def read_item(self, pid):
    ''' not called and may no longer be needed 
    '''
    palette = list()
    self.cursor.execute("""
SELECT fill, bg, opacity
FROM palette
WHERE pid = %s;""", [pid])
    palette = self.cursor.fetchone()
    return palette

  def read_pid(self, palette):
    palette.append(self.ver)
    self.cursor.execute("""
SELECT pid
FROM palette
WHERE fill = %s
AND bg = %s
AND opacity = %s
AND ver = %s;""", palette)
    pid = self.cursor.fetchone()
#    return pid[0] if pid else None
    if pid:
      return pid[0]
    else:
      raise ValueError(f"unable to find pid for {palette}")

  def read_any(self, ver):
    self.cursor.execute("""
SELECT fill, bg, opacity
FROM palette
WHERE ver = %s
ORDER BY random() LIMIT 1;""", [ver])
    return list(self.cursor.fetchone())

  def read_palette(self, ver):
    self.cursor.execute("""
SELECT fill, opacity, bg
FROM palette
WHERE ver = %s;""", [ver])
    self.palette = self.cursor.fetchall()
    self.complimentary = dict()
    self.cursor.execute("""
SELECT fill, bg, complimentary
FROM palette
WHERE ver = %s;""", [ver])
    for row in self.cursor.fetchall():
      fill, bg, compliment = row
      self.complimentary[fill] = compliment
      self.complimentary[bg] = compliment
    self.cursor.execute("""
SELECT DISTINCT(fill)
FROM palette
WHERE ver = %s;""", [ver])
    self.fill = [f[0] for f in self.cursor.fetchall()]
    self.cursor.execute("""
SELECT DISTINCT(bg)
FROM palette
WHERE ver = %s;""", [ver])
    self.backgrounds = [bg[0] for bg in self.cursor.fetchall()]

  def read_opacity(self, fill=None, bg=None):
    if fill and bg: # opacity varies according to fill when ver is universal
      self.cursor.execute("""
SELECT DISTINCT(opacity)
FROM palette
WHERE fill = %s
AND bg = %s
AND ver = %s;""", [fill, bg, self.ver])
    else:
      self.cursor.execute("""
SELECT DISTINCT(opacity)
FROM palette
WHERE ver = %s;""", [self.ver])
    opacity = [o[0] for o in self.cursor.fetchall()]
    return opacity

  def read_colours(self):
    self.cursor.execute("""
SELECT fill
FROM colours;""", [])
    colours = [c[0] for c in self.cursor.fetchall()]
    return colours

  def load_palette(self, ver=None):
    ''' used to validate inputs from tmpfile
    '''
    ver = ver if ver else self.ver  # override for tester
    if ver is not None:  # universal is zero
      self.read_palette(ver)
      #print(len(self.palette))
      if len(self.palette) == 0:
        raise ValueError(f"what version are you on about {ver}")

  def generate_any(self, ver=None):
    ver = ver if ver else self.ver
    return dict(zip(['fill','bg','fill_opacity'], Palette.read_any(self, ver=ver)))

  def generate_one(self, ver=None, primary=None):
    ver = ver if ver else self.ver
    if primary:
      fill, bg, fo = primary['fill'], primary['bg'], primary['fill_opacity']
      one = self.complimentary[fill], self.complimentary[bg], fo
    else:
      one = Palette.read_any(self, ver=ver)
    return dict(zip(['fill','bg','fill_opacity'], one))

  # TODO edge case where all values are valid but their combined value does not exit in palette
  def validate(self, cell, data):
    ''' apply rules for defined palette
    '''
    Geometry.validate(self, cell, data) 
    fo = float(data['fill_opacity'])
    so = float(data['stroke_opacity']) if data['stroke_opacity'] else None
    # print(f"{cell} v{self.ver}\tfo {fo} stroke {data['fill']} {data['bg']} {so}")
    if self.ver == 0: # override opacity because universal palette is a bit random
      self.opacity = self.read_opacity(fill=data['fill'], bg=data['bg'])
    if fo not in self.opacity: 
      raise ValueError(f"validation error: fill opacity >{cell}<")
    if so and so not in self.opacity: 
      raise ValueError(f"validation error: stroke opacity >{cell}< {so}: {self.opacity}")
    if data['fill'] not in self.fill: 
      raise ValueError(f"validation error: fill >{cell}<")
    if data['bg'] not in self.backgrounds: 
      raise ValueError(f"validation error: background >{cell}< ver: {self.ver}")
    if fo == 1 and data['fill'] == data['bg'] and data['stroke_width'] is None:
      print(f"WARNING: opaque fill on same background >{cell}< ver: {self.ver}")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Strokes(Palette):

  def __init__(self, ver):
    super().__init__(ver)

  def create(self, items):
    ''' each geometry in a cell has an optional stroke
    '''
    if len(items) == 4:
      sid = self.read_sid(strokes=items)
      if sid is None:
        self.cursor.execute("""
INSERT INTO strokes (sid, fill, width, dasharray, opacity)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING sid;""", items)
        sid = self.cursor.fetchone()[0]
    else:
      raise ValueError('need 4 items to create a stroke')
    return sid

  def read(self, sid):
    if sid:
      strokes = list()
      self.cursor.execute("""
SELECT fill, width, dasharray, opacity
FROM strokes
WHERE sid = %s;""", [sid])
      strokes = self.cursor.fetchone()
      return strokes
    else:
      raise ValueError("need a sid to find a stroke")

  def read_sid(self, strokes):
    self.cursor.execute("""
SELECT sid
FROM strokes
WHERE fill = %s
AND width = %s
AND dasharray = %s
AND opacity = %s;""", strokes)
    sid = self.cursor.fetchone()
    return sid[0] if sid else None

  def read_any(self, ver, opacity):
    self.cursor.execute("""
SELECT s.fill, width, dasharray, s.opacity
FROM palette as p
LEFT OUTER JOIN strokes as s ON p.fill = s.fill OR p.bg = s.fill
WHERE ver = %s
AND s.opacity = %s
GROUP BY sid
ORDER BY random() LIMIT 1;""", [ver, opacity])
    return list(self.cursor.fetchone())

  def generate_one(self, stroke=None):
    ''' given a pair of cells, treat the second with a complimentary stroke
    '''
    #print(f"one v {self.ver} so {self.opacity}")
    data = dict()
    if stroke:
      data = stroke
      fill = stroke['stroke']
      data['stroke'] = self.complimentary[fill]
    else:
      data = dict(zip(['stroke','stroke_width','stroke_dasharray','stroke_opacity'], self.read_any(self.ver, random.choice(self.opacity))))
    return data

  def generate_any(self, ver=None):
    ver = ver if ver else self.ver # override for tester
    #print(f"any v {ver} so {self.opacity}")
    empty = { 'stroke': None, 'stroke_width': None, 'stroke_dasharray': None, 'stroke_opacity': None }
    # TODO stroke or not should be consistent across all cells in view ?
    YN = random.choice([True, False]) # fifty fifty chance to get a stroke
    return dict(
      zip(['stroke','stroke_width','stroke_dasharray','stroke_opacity'], self.read_any(ver, random.choice(self.opacity)))
    ) if YN else empty

  # TODO if width is 0 then all stroke attributes should be null
  def generate_new(self):
    ''' totally rnd no control whatsoever! Only called by celldata.py
    '''
    width = random.choice(self.zeroten)
    return {
      'fill': random.choice(self.palette)[2], # background from ver
      'width': width,
      'dasharray': random.choice(self.zeroten),
      'opacity': random.choice(self.palette)[1]
    }

  def validate(self, cell, data):
    ''' apply rules for defined palette and then these for stroke
    '''
    Palette.validate(self, cell, data)
    if 'width' in data:
      sw = int(data['width'])
      if sw < min(self.zeroten) or sw > max(self.zeroten):
        raise ValueError(f"validation error: stroke width >{cell}<")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Cell(Strokes):
  ''' a cell is a member of a block and contains geometries, shapes and strokes
  '''
  def __init__(self, ver=None):
    super().__init__(ver)

  def create(self, digest, items):
    ''' create a cell by joining a view with geometry and style entries
    '''
    ok = True # used only by unit test
    cell = items.pop(0) # ignore first item cell
    gid = Geometry.read_gid(self, item=items[:4]) 
    pid = Palette.read_pid(self, palette=items[4:7])
    sid = Strokes.read_sid(self, strokes=items[7:])
    # print(digest, cell, gid, pid, sid)
    try:
      self.cursor.execute("""
INSERT INTO cells (view, cell, gid, pid, sid)
VALUES (%s, %s, %s, %s, %s);""", [digest, cell, gid, pid, sid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      ok = False
    return ok

  def generate(self, top, axis=None, facing_all=False, facing=None, primary=None, stroke=None):
    #print(f"a {axis} t {top} p {facing} p {primary} s {stroke}")
    if axis:
      g = Geometry.generate_one(self, axis, top, facing)
      p = Palette.generate_one(self, primary=primary)
      s = Strokes.generate_one(self, stroke=stroke)
    else:
      if facing_all:
        g = Geometry.generate_all(self, top)
      else:
        g = Geometry.generate_any(self, top)
      p = Palette.generate_any(self)
      s = Strokes.generate_any(self)
    if self.ver == 0 and s['stroke_width']: # hack to overcome uneven opacity values in universal palette
      s['stroke_opacity'] = random.choice(Palette.read_opacity(self, fill=p['fill'], bg=p['bg']))
    self.data = g | p | s

  def validate(self, celldata):
    self.load_palette()
    [Strokes.validate(self, c, celldata[c]) for c in celldata]
  '''
  the
  end
  '''
