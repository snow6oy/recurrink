import xml.etree.ElementTree as ET
import pprint
from tmpfile import TmpFile
from cell import Palette, Strokes
from colorsys import rgb_to_hsv, hsv_to_rgb
pp = pprint.PrettyPrinter(indent = 2)

'''
                                ver     f_name  view
1: db to tmpfile                y       y       -
2: tmpfile to svg               -       y       -       
3: create palette from tmpfile  -       y       -
7: export view as tmp/pal       -       -       y
8: compare palettes             -       y       y

move to t/palette
4: unit tests fg/bg relations   -       y       -

move to recurrink
6: upd db.cells opacity         y       -       -
9: upd db.cells swap pal view   y       y       y

delete
5: upd pal from  tmpfile        -       y       -
'''


class PaletteMaker:
  ''' tool for updating tutorial/palette.pdf
  '''
  def root(self, w, h):
    ns = '{http://www.w3.org/2000/svg}'
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      xmlns:svg="http://www.w3.org/2000/svg" 
      viewBox="0 0 {w} {h}" width="{w}px" height="{h}px"></svg>
    ''')
    #ET.dump(root)
    self.ns = ns
    self.root = root

  def grid(self, palette):
    ''' create a grid with metadata
    '''
    grid = list() # list of rows on y axis
    maxrow = 0
    for p in palette:
      if len(p) == 4:
        fill, opacity, bg, ct = p
      else:
        fill, opacity, bg = p
        ct = None
      row = list()
      if ct and ct == 'y':
        row.append({ 'fg': fill, 'op': 1, 'bg': None, 'ct': True })
      else:
        row.append({ 'fg': fill, 'op': 1, 'bg': None, 'ct': False })
      row.append({ 'fg': bg, 'op': 1, 'bg': None, 'ct': False })
      if float(opacity) < 1:
        row.append({ 'fg': fill, 'op': opacity, 'bg': bg, 'ct': False })
      if len(row) > maxrow:
        maxrow = len(row)
      grid.append(row)
    return maxrow, grid

  def make(self, grid, verbose=False):
    for y, col in enumerate(grid):
      for x, row in enumerate(col):
        xid = f"{x:02}-{y:02}"
        if verbose:
          print(xid, end=' ', flush=True)
        if row['fg']:
          self.color(xid, row['fg'], '1.0', x, y)
        if row['bg']:
          self.color(xid, row['bg'], row['op'], x, y)
      if verbose:
        print()
    txtg = ET.SubElement(self.root, f"{self.ns}g", id="0")
    txtg.set("style", "fill:#FFF;stroke:#000;stroke-width:0.1;")
    for y, col in enumerate(grid):
      for x, row in enumerate(col):
        txt = row['op'] if row['bg'] else row['fg']
        if row['ct'] == True:
          txt += ' *'
        if txt:
          self.label(txtg, txt, x, y, xid)

  def label(self, txtg, text, x, y, xid):
    t = ET.SubElement(txtg, f"{self.ns}text", id=xid)
    t.text = str(f'{text}')
    tx = (x * 60) + 10
    ty = (y * 60) + 50
    t.set("x", str(tx))
    t.set("y", str(ty))

  def color(self, xid, fill, opacity, x, y):
    g = ET.SubElement(self.root, f"{self.ns}g", id=f"g-{xid}")
    style = f"fill:{fill};fill-opacity:{opacity};stroke:#FFF;stroke-width:1"
    g.set("style", style)
    rect = ET.SubElement(g, f"{self.ns}rect", id=f"r-{xid}")
    rect.set("x", str(x * 60))
    rect.set("y", str(y * 60))
    rect.set("width", "60")
    rect.set("height", "60")

  def write(self, ver):
    tree = ET.ElementTree(self.root)
    ET.indent(tree, level=0)
    tree.write(f'/tmp/{ver}.svg')

  def table(self, palette):
    ''' make document source for palette.pdf
    '''
    xid = 0
    for p in palette:
      xid += 1
      print(f'{xid:02} fill: {p[0]} opacity: {p[1]} bg: {p[2]}')
 
  def create_colour_table(self, colours):
    sql = "'),\n('".join(colours)
    print(f"INSERT INTO colours (fill) VALUES \n('{sql}');")

  def create_palette_table(self, palette, ver, colours):
    ''' print a SQL string to STDOUT
    '''
    vals = str()
    for col in colours:
      vals += f"('{col}'),\n" 
    vals = vals[:-2]
    if len(colours):
      print(f"INSERT INTO colours (fill) VALUES \n{vals};")
    vals = str()
    for p in palette:
      fill, o, bg = p
      rn = self.relation(fill, bg)
      vals += f"({ver}, '{fill}', '{bg}', '{o}', '{rn}'),\n"
    vals = vals[:-2]
    print(f"INSERT INTO palette (ver, fill, bg, opacity, relation) VALUES \n{vals};")

  def update_palette_table(self, palette, ver):
    ''' one-off migration to replace compliment with relation
    '''
    for p in palette:
      fill, o, bg = p
      #print(f"fill {fill} bg {bg} o {o}")
      if o == '1.0':
        rn = self.relation(fill, bg)
        print(f"UPDATE palette SET relation = {rn} WHERE ver = {ver} AND fill = '{fill}' AND bg = '{bg}' and opacity = 1;")

  def export_txtfile(self, palname, palette):
    ''' write paldata to a tab separated text file
    '''
    #pp.pprint(palette)
    if len(palette) == 0:
      raise ValueError(f"{palname} is empty")
    with open(f"/tmp/{palname}.txt", 'w') as f:
      print("\t".join(['fill', 'opacity', 'background']), file=f)
      for pal in palette:
        line = [str(p) for p in pal] # convert everything to string
        print("\t".join(line), file=f)  # flush=True)

  def import_txtfile(self, palname):
    with open(f"/tmp/{palname}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    return data

  def rgb_int(self, r, g, b):
    ''' the compliment of #dc143c is #14dcb4
      https://www.w3schools.com/colors/colors_hexadecimal.asp
      https://www.educative.io/answers/how-to-convert-hex-to-rgb-and-rgb-to-hex-in-python
      https://stackoverflow.com/questions/40233986/python-is-there-a-function-or-formula-to-find-the-complementary-colour-of-a-rgb
      returns RGB components of complementary color as int
    '''
    hsv = rgb_to_hsv(r, g, b)
    rgb_float = hsv_to_rgb((hsv[0] + 0.5) % 1, hsv[1], hsv[2])
    return [int(f) for f in rgb_float]

  def hex_rgb(self, hexstr):
    ''' slice into a list e.g. ['dc', '14', '3c']
    '''
    hexitems = [hexstr[1:3], hexstr[3:5], hexstr[5:]]
    # convert to base 16
    return [int(h,16) for h in hexitems]

  def relation(self, fill, bg):
    if len(fill) ==4:
      fill = f"#{fill[1]*2}{fill[2]*2}{fill[3]*2}".lower()
    if len(bg) ==4:
      bg = f"#{bg[1]*2}{bg[2]*2}{bg[3]*2}".lower()
    s = self.secondary(fill)
    #print(f"fill {fill} bg {bg} secondary {s}")
    if bg == fill:
      return 1
    elif bg == s:
      return 2
    else:
      return 0

  def secondary(self, fill=None):
    if fill:
      r, g, b = self.hex_rgb(fill)
      R, G, B = self.rgb_int(r, g, b)
      #return (fill, f'#{R:02x}{G:02x}{B:02x}')
      return f'#{R:02x}{G:02x}{B:02x}'
    else:
      raise ValueError('fill is required')

  def colour_check(self, p, palette):
    ''' compare the new palette against the main colour list
        return a list of those that are missing
    '''
    colours = p.read_colours()
    fill = set([p[0] for p in palette])
    backgrounds = set([p[2] for p in palette])
    for c in colours:
      if c in fill:
        fill.remove(c)
      if c in backgrounds:
        backgrounds.remove(c)
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

  def find_opacity(self, ver, tc, pal):
    ''' find the nearest opacity to the one we want to deprecate
        return the nearest op and pid, if it already exists in db
    '''
    old_fo = tc[1]
    available = pal.read_cleanpids([tc[0], tc[2]])
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

  def cmp_pal(self, p1, p2):
    #pp.pprint(p1)
    #pp.pprint(p2)
    same = 0
    for x in p1:
      for y in p2:
        if x[0] == y[0] and x[1] == y[1] and x[2] == y[2]:
          # print(x)
          same += 1
    return same

if __name__ == '__main__':
  pmk = PaletteMaker()
  friendly_name=['universal', 'colour45', 'htmstarter', 'jeb', 'whitebossa']
  ver = 4
  fn = friendly_name[ver] if False else '0b396143d41f9dadb07c0fb3b47446df'
  #'15ff3a9dd88436a0fffa87aad8904784'
  opt = 9
  p = Palette(ver=ver)
  if opt == 1: # db to tmpfile
    p.load_palette(ver=ver)
    pmk.export_txtfile(fn, p.palette)
  elif opt == 2: # tmpfile to svg
    palette = pmk.import_txtfile(fn)
    x, grid = pmk.grid(palette)
    #pp.pprint(grid)
    pmk.root(x * 60, len(grid) * 60)
    pmk.make(grid)
    pmk.write(fn)
  elif opt == 3: # tmpfile to sql
    palette = pmk.import_txtfile(fn)
    missing_colours = pmk.colour_check(p, palette)
    #print(missing_colours)
    #compliment = pmk.compliment(palette)
    #TODO get new colours pmk.create_colour_table(s.colours)
    pmk.create_palette_table(palette, ver, missing_colours)
  elif opt == 4: # run some compliment tests
    # DC143C crimson #C71585 mediumvioletred #FFA500 orange #32CD32 limegreen #4B0082 indigo
    [print(f, pmk.secondary(f)) for f in ['#dc143c', '#c71585', '#ffa500' ,'#32cd32', '#4b0082']]
    [print(f, pmk.secondary(f)) for f in ['#ff0000', '#ffff00', '#0000ff' ,'#ffffff', '#000000']]
  elif opt == 5: # tmpfile to sql
    palette = pmk.import_txtfile(fn)
    pmk.update_palette_table(palette, ver)
  elif opt == 6: # collapse opacity
    # op, pid = pmk.find_opacity(ver, ['#FFA500', 0.9, '#000'], p)
    # op, pid = pmk.find_opacity(ver, ['#CCC', 0.9, '#9ACD32'], p)
    # op, pid = pmk.find_opacity(ver, ['#C71585', 0.6, '#FFF'], p)
    # print(0.6, op, pid) 
    pmk.collapse_opacity(ver, p)
  elif opt == 7: # export view as palette
    palette = p.read_view(fn) # TODO Palette was initialised with ver but it was ignored. Hmmm
    # pp.pprint(set(palette))
    pmk.export_txtfile(fn, set(palette)) # need to flaten as same PID can belong to many cells
  elif opt == 8: # compare palettes
    new_pal = pmk.import_txtfile(fn)
    candidate = pmk.import_txtfile(friendly_name[ver])
    cmp = pmk.cmp_pal(new_pal, candidate)
    print(f"{len(new_pal):3d} {fn}")
    print(f"{len(candidate):3d} {friendly_name[ver]}")
    print(f"{cmp:3d} matching palette entries")
  elif opt == 9:
    tf = TmpFile()
    model = 'bossa' # TODO obtain from view
    celldata = tf.read(model, output=list())
    numupdated = p.swap_palette(celldata, ver, fn)
    print(f"{numupdated} pids were migrated to {friendly_name[ver]}")
  else:
    print("9 is the Very Last option")
