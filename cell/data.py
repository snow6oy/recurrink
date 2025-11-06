import random
import pprint
import psycopg2
from config import *
from .shape import *
from .geometry import Geometry
from .palette import Palette
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Strokes(Palette):

  def __init__(self, ver):
    super().__init__(ver)

  def create(self, item):
    ''' each geometry in a cell has an optional stroke
    '''
    if len(item) == 4:
      sid = self.readSid(item)
      if sid is None:
        print(f'adding {item}')
        self.cursor.execute("""
INSERT INTO strokes (sid, fill, width, dasharray, opacity)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING sid;""", item)
        sid = self.cursor.fetchone()[0]
    else:
      raise ValueError('need 4 vals in an item to create a stroke')
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

  def readSid(self, stroke):
    ''' palswap and recurrink send dicts and lists :/
    '''
    if isinstance(stroke, dict): # order is important
      item = [
        stroke['fill'], stroke['width'],stroke['dasharray'], stroke['opacity'] 
      ]
    else:
      item = stroke
    self.cursor.execute("""
SELECT sid
FROM strokes
WHERE fill = %s
AND width = %s
AND dasharray = %s
AND opacity = %s;""", item)
    sid = self.cursor.fetchone()
    return sid[0] if sid else None

  def swapSid(self, sids, ver, rink):
    ''' WARN: we break the golden "Rinks Are Immutable" rule
    '''
    for label in sids: # send uniq pids for update
      new = sids[label]
      ''' print(f"{rink=} {new=} {label=}")
      '''
      self.cursor.execute("""
UPDATE cells 
SET sid = %s 
WHERE view = %s 
AND cell = %s;""", 
        [new, rink, label]
      )
    return self.cursor.rowcount

  def updateSids(self, swp, celldata):
    ''' insert new SID unless exists already
    '''
    sids = dict()
    for label in celldata:
      if 'stroke' not in celldata[label]: continue
      old_stroke = celldata[label]['stroke']
      item = [
        swp[old_stroke].lower(),
        celldata[label]['stroke_width'],
        celldata[label]['stroke_dasharray'],
        celldata[label]['stroke_opacity']
      ]
      sid = self.readSid(item)
      if sid: sids[label] = sid
      else:
        sid = self.create(item)
        sids[label] = sid
    return sids
  

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
    if 'stroke_width' in data: 
      sw = int(data['stroke_width'])
      if sw < min(self.zeroten) or sw > max(self.zeroten):
        raise ValueError(f"validation error: stroke width >{cell}<")
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class CellData(Strokes):
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)
  ''' a cell is a member of a block and contains geometries, shapes and strokes
  '''
  def __init__(self, ver=None):
    super().__init__(ver)

  def create(self, digest, label, data):
    ''' create a cell by joining a view with geometry and style entries
    '''
    ok = True # used only by unit test
    gid = Geometry.read_gid(self, data['geom']) 
    pid = Palette.readPid(self, self.ver, data['color'])
    if pid is None: return None # ignore empty background cell
    if 'stroke' in data: 
      sid = Strokes.readSid(self, data['stroke'])
    else:                
      sid = None
    try:
      self.cursor.execute("""
INSERT INTO cells (view, cell, gid, pid, sid)
VALUES (%s, %s, %s, %s, %s);""", [digest, label, gid, pid, sid])
    except psycopg2.errors.UniqueViolation:  # 23505 
      if self.VERBOSE: print(f'{digest} {label} {gid=} {pid=} {sid=}')
      return False
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
