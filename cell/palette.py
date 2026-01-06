import pprint
import psycopg2
from config import *
from .geometry import Geometry
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Palette(Geometry):

  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)
  BADLEN  = {            # any change here to be done in block.palette too
    '#FFF': '#ffffff',
    '#CCC': '#cccccc',
    '#000': '#000000',
    '#F00': '#ff0000',
    '#FF0': '#ffff00',
    '#00F': '#0000ff',
    '#F0F': '#ff00ff',
    '#0FF': '#000fff'
  }

  def __init__(self, ver=None):
    super().__init__()
    self.ver = ver # None is not a good default (better to override)
    self.opacity = self.read_opacity()  # between 0 and 1 check MDN
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

  def createPaletteEntry(self, palette):
    ''' ver should be ID from inkpal table
        palette is a list of lists used to create the colour entries
    '''
    ver, fill, opacity, bg, relation = palette
    pid   = self.readPid(ver, {'fill':fill, 'background':bg, 'opacity':opacity})
    if pid: return pid
    self.cursor.execute("""
INSERT INTO palette (ver, fill, bg, opacity, relation) 
VALUES (%s, %s, %s, %s, %s)
RETURNING pid;""", 
      [ver, fill, bg, opacity, relation]
    )
    return self.cursor.fetchone()[0]

  def updatePids(self, ver, swp, celldata):
    ''' either get or set pids for new pal
        return pids[a] = new_pid
    ''' 
    pids = dict()

    for label in celldata:
      fg = celldata[label]['fill']
      bg = celldata[label]['bg']
      color = {
              'fill': swp[fg],
        'background': swp[bg],
           'opacity': 0.5
      }
      pid = self.readPid(ver, color)
      if pid: pids[label] = pid
      else:
        entry = (tuple([ver, swp[fg], 0.5, swp[bg], 0]))
        pid   = self.createPaletteEntry(entry)
        pids[label] = pid
    return pids

  def swapPalette(self, pids, ver, rink):
    ''' WARN: we break the golden "Rinks Are Immutable" rule
      the reason is that collapsing universal palette requires 
      rinks to be moved to a new palette
      so we update a view generated with universal palette to use another
    '''
    for label in pids: # send uniq pids for update
      new = pids[label]
      ''' print(f"{rink=} {new=} {label=}")
      '''
      self.cursor.execute("""
UPDATE cells 
SET pid = %s 
WHERE view = %s 
AND cell = %s;""", 
        [new, rink, label]
      )
    rownum = self.cursor.rowcount
    self.cursor.execute("""
UPDATE views 
SET ver = %s 
WHERE view = %s;""", 
      [ver, rink]
    )
    return self.cursor.rowcount + rownum

  def colour_check(self, palette):
    ''' compare the new palette against the main colour list
        return a list of those that are missing
    '''
    colours     = self.read_colours()
    #self.pp.pprint(colours)
    fill        = set([p[0] for p in palette])
    backgrounds = set([p[2] for p in palette])
    for c in colours:
      if c in fill:               fill.remove(c)
      if c in backgrounds: backgrounds.remove(c)
    missing = list(fill) + list(backgrounds)
    return set(missing)

  def collapse_opacity(self, ver, pal):
    ''' for each opacity to be collapsed
        select palette entry with bad opacity
        find nearest pid
        update cells table so view with old pid uses new pid
    '''
    pal.load_palette(ver=ver)
    #new_pid = pal.read_pid(['#C71585', '#FFF', '0.9'])
    for old_fo in [0.6]:  # 9, 0.7, 0.4, 0.3, 0.1]:
      #print(old_fo)
      to_clean = [p for p in pal.palette if p[1] == old_fo]
      for tc in to_clean:
        old_pid = pal.read_pid([tc[0], tc[2], tc[1]])
        new_opacity, new_pid = self.find_opacity(ver, tc, pal)
        if new_pid:
          print(f"UPDATE cells SET pid = {new_pid} WHERE pid = {old_pid};")
        else:
          pass
          #relation = self.relation(tc[0], tc[2])
          #print(f"INSERT INTO palette (ver, fill, bg, opacity, relation) VALUES (0,'{tc[0]}', '{tc[2]}', {new_opacity}, {relation});")

  def find_opacity(self, tc):
    ''' find the nearest opacity to the one we want to deprecate
        return the nearest op and pid, if it already exists in db
    '''
    old_fo = tc[1]
    available = self.read_cleanpids([tc[0], tc[2]])
    #pp.pprint(available)
    candidates = list()
    for candidate in [1, 0.8, 0.5, 0.2]:
      if candidate > old_fo:
        nearest = (candidate * 10) - (old_fo * 10)
      else:
        nearest = (old_fo * 10) - (candidate * 10)
      pid = None
      for a in available:
        if candidate == a[1]: # compare opacities
          pid = a[0]
          break
      candidates.append([candidate, int(nearest), pid])
    new_pid = sorted(candidates, key=lambda x: x[1], reverse=False)
    #pp.pprint(new_pid)
    return new_pid[0][0], new_pid[0][2]

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
    palette = self.cursor.fetchall()
    strokes = self.readStrokeFill(view)
    return palette + strokes

  def readStrokeFill(self, view):
    ''' export strokes for block palette
  
    '''
    palette = list()
    self.cursor.execute("""
SELECT fill, opacity, NULL
FROM cells, strokes 
WHERE cells.sid=strokes.sid 
AND view = %s;""", [view])
    palette = self.cursor.fetchall()
    return palette

  def readPid(self, ver, color): 
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
    if pid: return pid[0]
    elif self.VERBOSE: print(f"unable to find pid for {palette}")
    
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
    ''' compliment is defined as any relation 
        whether 1 same:same or 2 same:opposite
        once the use-cases are defined these should be split
        colours with multiple palette entries 
        have the relation entry as priority
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
    self.read_compliment(ver) # who calls here ???
    return self.palette 

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

  def penNames(self, penam, gpldata, ver=0):
    ''' pen names keyed by ver:hex
    '''
    if ver > 0: # grab everything and run
      self.cursor.execute("""
SELECT * 
FROM pens
WHERE ver = %s;""", [ver])
      return self.cursor.fetchall()
    else:
      ver = self.verByPenam(penam)
      for hexstr in gpldata:
        self.cursor.execute("""
INSERT INTO pens (ver, fill, penam)
VALUES (%s, %s, %s);""", 
          [ver, hexstr, gpldata[hexstr]]
        )

  def friendlyPenNames(self):
    ''' friendly names of pens
    '''
    self.cursor.execute("""
SELECT gplfile
FROM inkpal
ORDER BY ver;""", [])
    fnam = [name[0] for name in self.cursor.fetchall()]
    fnam.insert(0, None) # avoid conditional zero error
    return fnam

  def loadPalette(self, ver=None):
    ''' used to validate inputs from tmpfile
    '''
    ver = ver if ver in range(99) else self.ver  # override for tester
    self.read_palette(ver)
    if len(self.palette) == 0:
      raise ValueError(f"what version are you on about {ver}")
    uniqfill = set()
    for p in self.palette:  # align with Pydantic.Color
      fg, op, bg = p
      if fg in self.BADLEN: fg = self.BADLEN[fg]
      uniqfill.add(fg.lower())
      if bg in self.BADLEN: bg = self.BADLEN[bg]
      if bg: uniqfill.add(bg.lower())
    self.uniqfill = uniqfill

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

  def validate(self, label, cell):
    ''' raise error unless given data exists in palette
    '''
    if 'geom' in cell:
      Geometry.validate(self, label, cell['geom']) 
    if 'color' in cell:
      fg = cell['color']['fill']
      op = float(cell['color']['opacity'])
      bg = cell['color']['background']
      if op < 0 or op > 1: 
        raise ValueError(f"validation error: >{label}< {op=} not ok {self.ver}")
      elif fg not in self.uniqfill:
        raise ValueError(f"validation error: >{label}< {fg=} not in {self.ver}")
      elif bg and bg not in self.uniqfill:
        raise ValueError(f"validation error: >{label}< {bg=} not in {self.ver}")
    if 'stroke' in cell and cell['stroke']: 
      f = cell["stroke"]['fill']
      if f not in self.uniqfill:
        raise ValueError(f"cell: >{label}< {f} stroke not in {self.ver}")

'''
the
end
'''
