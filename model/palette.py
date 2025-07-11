import xml.etree.ElementTree as ET
import math

class SvgPalette:
  ''' tool for generating tmp/PALETTE.svg
  '''

  def render(self, fn, palette):
    ''' entry point
    '''
    gs      = self.gridsize(3, len(palette))
    x, grid = self.grid(palette, gs)
    self.root(gs[0] * 60, gs[1] * 60)
    self.make(grid, verbose=True)
    self.write(fn)

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
    tree.write(f'tmp/{ver}.svg')

'''
the
end
'''
