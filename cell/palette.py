import pprint
import psycopg2
from config import *
from .geometry import Geometry
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Palette(Geometry):

  VERBOSE = True

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

  def friendlyPenNames(self):
    ''' friendly names of pens
    '''
    self.cursor.execute("""
SELECT gplfile
FROM inkpal;""", [])
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
    [uniqfill.add(p[0]) for p in self.palette]
    [uniqfill.add(p[2]) for p in self.palette]
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
    if 'stroke' in cell: 
      f = cell["stroke"]['fill']
      if f not in self.uniqfill:
        raise ValueError(f"cell: >{label}< {f} stroke not in {self.ver}")

'''
the
end
'''
