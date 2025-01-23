import xml.etree.ElementTree as ET
import math
import pprint
from block import TmpFile
#from cell import Palette, Strokes
from colorsys import rgb_to_hsv, hsv_to_rgb
pp = pprint.PrettyPrinter(indent = 2)

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
    txtg.set("style", "fill:#FFF;stroke:#000;stroke-width:0.2;")
    for y, col in enumerate(grid):
      for x, row in enumerate(col):
        txt = row['op'] if row['bg'] else row['fg']
        #if row['ct'] == True:
        #  txt += ' *'
        if txt:
          self.label(txtg, txt, x, y, xid)

  def grid(self, palette, gridsize):
    ''' create a grid with metadata
        x,y defines the grid size
        i,j refer to palette entries
    '''
    grid = list() # list of rows on y axis
    maxrow = 3
    i = j = 0
    if gridsize[2]: # apply padding
      [palette.append([None, 1, None]) for pad in (range(gridsize[2]))]

    for y in range(gridsize[1]):
      row = list()
      for x in range(gridsize[0]):
        i = i + 1 if x % maxrow else 0 # count 0,1,2 in relation to x
        #print(f"{i} {j}")
        p = palette[j][i]
        if i == 0: 
          fg = p
          row.append({ 'fg': fg, 'op': 1, 'bg': None })
        elif i == 1:
          if float(p) < 1:
            bg = palette[j][2]
            row.append({ 'fg': fg, 'op': p, 'bg': bg })
          else:
            row.append({ 'fg': None, 'op': None, 'bg': None })
        if i == 2:
          row.append({ 'fg': p, 'op': 1, 'bg': None })
          #print(f"{j}", end= ' ', flush=True)
        j = j + 1 if i == 2 else j
      grid.append(row)
      #print()
    return maxrow, grid

  def gridsize(self, x, y):
    ''' from the maxrow size x, calculate y 
        result should be a rectangle with slightly more cols than rows
        NOTE that int() is used because round() up
        yields a VERY NASTY index out of range error
    '''
    padding = 0
    cells = x * y
    square_root = round(math.sqrt(cells))
    #print(f"x1 {x} y1 {y} c {cells} sqrt {square_root}")
    for i in range(square_root, y):
      n = i % x
      if not n:
        x = i
        break
    y = int(cells / x)
    slots = x * y     # do we have stragglers?
    if cells > slots: # add extra row + padding to align with x
      y += 1
      padding = x - ((cells - slots) / 3)
    #print(f"x2 {x} y2 {y} s {slots} p{int(padding)}")
    #print()
    return x, y, int(padding)

  def label(self, txtg, text, x, y, xid):
    t = ET.SubElement(txtg, f"{self.ns}text", id=xid)
    t.text = str(f'{text}')
    tx = (x * 60) + 5 
    ty = (y * 60) + 50
    t.set("x", str(tx))
    t.set("y", str(ty))

  def color(self, xid, fill, opacity, x, y):
    g = ET.SubElement(self.root, f"{self.ns}g", id=f"g-{xid}")
    style = f"fill:{fill};fill-opacity:{opacity};stroke:#FFF;stroke-width:5"
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
