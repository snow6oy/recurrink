import xml.etree.ElementTree as ET
import pprint
from cell import Palette, Strokes
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
      row.append({ 'fg': fill, 'op': 1, 'bg': None })
      row.append({ 'fg': bg, 'op': 1, 'bg': None })
      if float(opacity) < 1:
        row.append({ 'fg': fill, 'op': opacity, 'bg': bg })
      if ct:
        row.append({ 'fg': ct, 'op': 1, 'bg': None })  # compliment TODO
      if len(row) > maxrow:
        maxrow = len(row)
      grid.append(row)
    return maxrow, grid

  def make(self, grid):
    for y, col in enumerate(grid):
      for x, row in enumerate(col):
        xid = f"{x:02}-{y:02}"
        print(xid, end=' ', flush=True)
        if row['fg']:
          self.color(xid, row['fg'], '1.0', x, y)
        if row['bg']:
          self.color(xid, row['bg'], row['op'], x, y)
      print()
    txtg = ET.SubElement(self.root, f"{self.ns}g", id="0")
    txtg.set("style", "fill:#FFF;stroke:#000;stroke-width:0.1;")
    for y, col in enumerate(grid):
      for x, row in enumerate(col):
        txt = row['op'] if row['bg'] else row['fg']
        if txt:
          self.label(txtg, txt, x, y, xid)

  def label(self, txtg, text, x, y, xid):
    t = ET.SubElement(txtg, f"{self.ns}text", id=xid)
    t.text = str(f'{text}')
    tx = (x * 60) + 10
    ty = (y * 60) + 30
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

  def create_palette_table(self, palette, complimentary, ver):
    vals = str()
    for p in palette:
      fill, o, bg = p
      vals += f"({ver}, '{fill}', '{bg}', '{complimentary[fill]}', {o}),\n"
    print(f"INSERT INTO palette (ver, fill, bg, complimentary, opacity) VALUES \n{vals};")

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

if __name__ == '__main__':
  pmk = PaletteMaker()
  friendly_name=['universal', 'colour45', 'htmstarter', 'jeb']
  ver = 0
  opt = 2
  if opt == 1:
    p = Palette(ver=ver)
    p.load_palette(ver=ver)
    pmk.export_txtfile(friendly_name[ver], p.palette)
  elif opt == 2:
    palette = pmk.import_txtfile(friendly_name[ver])
    x, grid = pmk.grid(palette)
    #pp.pprint(grid)
    pmk.root(x * 60, len(grid) * 60)
    pmk.make(grid)
    pmk.write(friendly_name[ver])
  else:
    pmk = PaletteMaker(540, 300)
    #pmk.create_colour_table(s.colours)
    extra = pmk.extra_palette_table(p.fill)
    pmk.create_palette_table(extra, p.complimentary, 1)
    #pmk.create_strokes_table()
    #pp.pprint(s.palette)
    #pmk.table(s.palette)
