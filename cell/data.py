import random
import psycopg2
from model import Db
from .shape import *

class Geometry(Db):
  ''' Generate a geometry by selecting existing geometries from db
      Validate input geometries
  '''
  def __init__(self):
    super().__init__()
    self.attributes = {
      'shape': ['circle', 'line', 'square', 'triangl', 'diamond'],
      'facing': ['C','N', 'S', 'E', 'W'],
      'size': ['medium', 'large'],
      'top': [True, False]
    }
    self.flip = {
       'E': { 'N': 'S', 'S': 'N' },
       'N': { 'W': 'E', 'E': 'W' },
      'NE': { 'N': 'E', 'E': 'N' },
      'SW': { 'S': 'W', 'W': 'S' }
    }
    self.defaults = { 
      'shape':'square', 'size':'medium', 'facing':None, 'top':False 
    }

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

  def read_gid(self, geom):
    ''' in order to commit, the item must be converted to a gid
    '''
    item = [geom[k] for k in ['name', 'size', 'facing', 'top']]
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
WHERE facing = 'C'
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
    # makes western line and IT IS FINE
    geom[2] = flip[facing] if facing else geom[2] 
    geom[3] = top
    return dict(zip(['shape','size','facing','top'], geom))

  def validate(self, label, geom):
    if 'name' in geom: name = geom['name']
    else: raise ValueError(f"validation error: {label}")

    shapes = {
         'line': Rectangle(name),
         'edge': Rectangle(name),
       'square': Rectangle(name),
       'sqring': Rectangle(name),
       'gnomon': Gnomon(),
      'parabol': Parabola(),
      'triangl': Triangle(),
      'diamond': Diamond(),
       'circle': Circle()
    }
    shape  = shapes[name]
    errmsg = shape.validate(geom)
    if errmsg: raise ValueError(f"validation error {label}: {name} {errmsg}")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Palette(Geometry):

  def __init__(self, ver=0):
    super().__init__()
    self.ver = ver # universal is not a good default (better to override)
    self.opacity = self.read_opacity()
    self.zeroten = [n for n in range(1, 11)]


  ''' print a SQL string to STDOUT
  def create_colour_table(self, colours):
    sql = "'),\n('".join(colours)
    print(f"INSERT INTO colours (fill) VALUES \n('{sql}');")

  '''
  def create_colours(self, colours):
    ''' add new colour as required for palette creation
    '''
    if len(colours):
      for col in colours:
        self.cursor.execute("""
INSERT INTO colours (fill) VALUES (%s);""", [col])

  def create_palette_entry(self, palette):
    ''' ver should be next increment ID of palette
        palette is an array used to create the colour entries
    '''
    for p in palette: 
      ver, fill, opacity, bg, relation = p # re-order
      self.cursor.execute("""
INSERT INTO palette (ver, fill, bg, opacity, relation) VALUES (%s, %s, %s, %s, %s);
""", [ver, fill, bg, opacity, relation])

  def swap_palette(self, celldata, ver, view, old_ver=0):
    ''' WARN: we break the golden "Rinks Are Immutable" rule
      the reason is that collapsing universal palette requires 
      rinks to be moved to a new palette
      so we update a view generated with universal palette to use another
    '''
    # old_pid = self.read_pid(ver=old_ver, palette=['#FFF', '#9ACD32', '0.5'])
    pids = list()
    for items in celldata: # get old and new pids
      items.pop(0) # discard cell label 
      #print(items[4:7])
      pids.append(tuple([
        self.read_pid(ver=ver, palette=items[4:7]),
        view,
        self.read_pid(ver=old_ver, palette=items[4:7]) 
      ]))
    # set new pid 
    for new_old in set(pids): # send uniq pids for update
      print(f"new pid = {new_old[0]} view {new_old[1]} old pid = {new_old[2]}")
      self.cursor.execute("""UPDATE cells SET pid = %s WHERE view = %s AND pid = %s;""", new_old)
    self.cursor.execute("""UPDATE views SET ver = %s WHERE view = %s;""", [ver, view])
    return self.cursor.rowcount

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

  def read_view(self, view):
    ''' export palette to tmpfile based on view
    '''
    palette = list()
    self.cursor.execute("""
SELECT fill, opacity, bg
FROM cells, palette
WHERE cells.pid = palette.pid
AND view = %s;""", [view])
    # palette = [p[0] for p in self.cursor.fetchall()]
    palette = self.cursor.fetchall()
    return palette

  def read_pid(self, ver, color): 
    palette = [color[k] for k in ['fill', 'background', 'opacity']]
    palette.append(ver)
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

  def read_cleanpids(self, palette):
    ''' used to collapse opacity in universal palette
    '''
    self.cursor.execute("""
SELECT pid, opacity
FROM palette
WHERE ver = 1
AND fill = %s
AND bg = %s;""", palette)
    pids = self.cursor.fetchall()
    return pids

  def read_any(self, ver):
    #if ver not in range(9): ver = 1 # 10 has no entries
    self.cursor.execute("""
SELECT fill, bg, opacity
FROM palette
WHERE ver = %s
ORDER BY random() LIMIT 1;""", [ver])
    return list(self.cursor.fetchone())

  def read_compliment(self, ver):
    ''' compliment is defined as any relation whether 1 same:same or 2 same:opposite
        once the use-cases are defined these should be split
        colours with multiple palette entries have the relation entry as priority
    '''
    self.complimentary = dict()
    self.cursor.execute("""
SELECT fill, bg
FROM palette
WHERE ver = %s
ORDER BY relation;""", [ver])
    for row in self.cursor.fetchall():
      fill, bg = row
      self.complimentary[fill] = bg
      self.complimentary[bg] = fill

  def read_palette(self, ver):
    self.cursor.execute("""
SELECT fill, opacity, bg
FROM palette
WHERE ver = %s
ORDER BY relation, fill, opacity;""", [ver])
    self.palette = self.cursor.fetchall()
    self.read_compliment(ver)

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

  def verByPenam(self, penam):
    ''' return ver from a pen name e.g. stabilo68 returns 11
    '''
    self.cursor.execute("""
SELECT ver 
FROM inkpal 
WHERE gplfile = %s;""", [penam])
    row = self.cursor.fetchone()
    ver = row[0] if len(row) else None
    return ver

  def penNames(self, penam, gpldata):
    ''' pen names keyed by ver:hex
    '''
    ver = self.verByPenam(penam)
    if ver:
      for hexstr in gpldata:
        self.cursor.execute("""
INSERT INTO pens (ver, fill, penam)
VALUES (%s, %s, %s);""", 
          [ver, hexstr, gpldata[hexstr]]
        )

  def loadPalette(self, ver=None):
    ''' used to validate inputs from tmpfile
    '''
    ver = ver if ver in range(99) else self.ver  # override for tester
    self.read_palette(ver)
    if len(self.palette) == 0:
      raise ValueError(f"what version are you on about {ver}")

  def generate_any(self, ver=None):
    ver = ver if ver else self.ver
    return dict(
      zip(['fill','bg','fill_opacity'], 
      Palette.read_any(self, ver=ver))
    )

  def generate_one(self, ver=None, primary=None):
    ver = ver if ver else self.ver
    if primary:
      fill, bg, fo = primary['fill'], primary['bg'], primary['fill_opacity']
      one = self.complimentary[fill], self.complimentary[bg], fo
    else:
      one = Palette.read_any(self, ver=ver)
    return dict(zip(['fill','bg','fill_opacity'], one))



  # edge case where all values are valid but their combined value does not exit in palette
  def valzzzzz(self, cell, data):
    ''' apply rules for defined palette
    '''
    Geometry.validate(self, cell, data) 
    fo = float(data['fill_opacity'])
    so = float(data['stroke_opacity']) if data['stroke_opacity'] else None
    # print(f"{cell} v{self.ver}\tfo {fo} stroke {data['fill']} {data['bg']} {so}")
    if self.ver == 1: # override opacity as universal palette is a bit random
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
 
  def validate(self, label, cell):
    ''' raise error unless given data exists in palette
    '''
    if 'geom' in cell:
      Geometry.validate(self, label, cell['geom']) 
    if 'color' in cell:
      fo = float(cell['color']['opacity'])
      # '#' + cell['color']['fill'], fo, '#' + cell['color']['background']
      t  = tuple([cell['color']['fill'], fo, cell['color']['background']])
      if t not in self.palette:
        raise ValueError(f"validation error: >{label}< {t} not in {self.ver=}")
    if 'stroke' in cell:
      pass
      '''
      if 'opacity' in cell['stroke']: so = float(cell['stroke']['opacity'])
      else: so = None
      if (fo == 1 and so is None
        and cell['color']['fill'] == cell['color']['background']): 
          print(f"""
WARNING: opaque fill on same background >{cell}< ver: {self.ver}""")
      '''

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

  def read_sid(self, stroke):
    strokes = [stroke[k] for k in ['fill','width','dasharray','opacity']]
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
    ''' a side effect of adding new Inkscape palettes is that SELECT returned None
        the opacity limit has been relaxed so that init can work randomly
    AND s.opacity = %s
    ORDER BY random() LIMIT 1;""", [ver, opacity])
    '''
    if ver not in range(99): raise ValueError()
    self.cursor.execute("""
SELECT s.fill, width, dasharray, s.opacity
FROM palette as p
LEFT OUTER JOIN strokes as s ON p.fill = s.fill OR p.bg = s.fill
WHERE ver = %s
GROUP BY sid
ORDER BY random() LIMIT 1;""", [ver])
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
      data = dict(
        zip(['stroke','stroke_width','stroke_dasharray','stroke_opacity'], 
        self.read_any(self.ver, random.choice(self.opacity)))
      )
    return data

  def generate_any(self, ver=None):
    ver = ver if ver else self.ver # override for tester
    #print(f"any v {ver} so {self.opacity}")
    empty = { 'stroke': None, 'stroke_width': None, 'stroke_dasharray': None, 'stroke_opacity': None }
    # TODO stroke or not should be consistent across all cells in view ?
    YN = random.choice([True, False]) # fifty fifty chance to get a stroke
    return dict(
      zip(['stroke','stroke_width','stroke_dasharray','stroke_opacity'], 
      self.read_any(ver, random.choice(self.opacity)))
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
class CellData(Strokes):
  ''' a cell is a member of a block and contains geometries, shapes and strokes
  '''
  def __init__(self, ver=None):
    super().__init__(ver)

  def create(self, digest, label, data):
    ''' create a cell by joining a view with geometry and style entries
    '''
    ok = True # used only by unit test
    gid = Geometry.read_gid(self, data['geom']) 
    pid = Palette.read_pid(self, self.ver, data['color'])
    if 'stroke' in data: sid = Strokes.read_sid(self, data['stroke'])
    else:                sid = None
    #print(f'{digest} {label} {gid=} {pid=} {sid=}')
    try:
      self.cursor.execute("""
INSERT INTO cells (view, cell, gid, pid, sid)
VALUES (%s, %s, %s, %s, %s);""", [digest, label, gid, pid, sid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      ok = False
    return ok

  def generate(self, top, 
    axis=None, facing_all=False, facing=None, primary=None, stroke=None
  ):
    #print(f"a {axis} t {top} p {facing} p {primary} s {stroke}")
    if axis:
      g = Geometry.generate_one(self, axis, top, facing)
      p = Palette.generate_one(self, primary=primary)
      s = Strokes.generate_one(self, stroke=stroke)
    else:
      if facing_all: g = Geometry.generate_all(self, top)
      else:          g = Geometry.generate_any(self, top)
      p = Palette.generate_any(self)
      s = Strokes.generate_any(self)
    # hack to overcome uneven opacity values in universal palette
    if self.ver == 1 and s['stroke_width']: 
      s['stroke_opacity'] = random.choice(
        Palette.read_opacity(self, fill=p['fill'], bg=p['bg'])
      )
    self.data = g | p | s

  def validate(self, celldata):
    self.loadPalette()
    [Strokes.validate(self, c, celldata[c]) for c in celldata]

'''
  the
  end
'''
