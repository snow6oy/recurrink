import xml.etree.ElementTree as ET
import pprint
from db import Styles
from cells import Strokes
pp = pprint.PrettyPrinter(indent = 2)

class PaletteMaker:
  ''' tool for updating tutorial/palette.pdf
  '''
  def __init__(self, w, h):
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

  def make(self, palette):
    num_cols = 9
    xid = x = y = 0
    for p in palette:
      fill, opacity, bg = p
      for cell in range(2):
        g = ET.SubElement(self.root, f"{self.ns}g", id=f"g{xid}{cell}")
        if cell % 2:
          style = f"fill:{fill};fill-opacity:{opacity};stroke:#FFF;stroke-width:1"
        else:
          style = f"fill:{bg}"
        g.set("style", style)
        ''''''
        rect = ET.SubElement(g, f"{self.ns}rect", id=f"r{xid}")
        rect.set("x", str(x))
        rect.set("y", str(y))
        rect.set("width", "60")
        rect.set("height", "60")
      xid += 1
      x += 60
      #print(f'{xid}. {fill} {opacity} {bg}')
      if xid % num_cols == 0:
        x = 0
        y += 60

    ''' label cells 
    '''
    xid = x = y = 0
    txtg = ET.SubElement(self.root, f"{self.ns}g", id="0")
    txtg.set("style", "fill:#FFF;stroke:#000;stroke-width:0.1;")
    for p in palette:
      t = ET.SubElement(txtg, f"{self.ns}text", id=f"t{xid}")
      t.text = str(f'{(xid + 1):02}')
      tx = x + 10
      ty = y + 30
      t.set("x", str(tx))
      t.set("y", str(ty))
      xid += 1
      x += 60
      #print(f'{xid}. {fill} {opacity} {bg}')
      if xid % num_cols == 0:
        x = 0
        y += 60

  def write(self, ver):
    tree = ET.ElementTree(self.root)
    tree.write(f'tutorial/palette_{ver}.svg')

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

  def create_strokes_table(self):
    ''' oneoff creation made 300 unique strokes from 1171 Styles()
    '''
    sk = Strokes()
    with open('sql/strokes.txt') as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    for stroke in data:
      sid = sk.create(stroke)
      print(sid)

if __name__ == '__main__':
  s = Styles()
  ver = 'htmstarter'
  #ver='colour45'
  s.set_spectrum(ver=ver)
  #xml = PaletteMaker(300, 60)
  xml = PaletteMaker(540, 300)
  #xml.create_colour_table(s.colours)
  #xml.create_palette_table(s.palette, s.complimentary, 2)
  #xml.create_strokes_table()
  #pp.pprint(s.palette)
  #xml.make(s.palette)
  #xml.write(ver)
  #xml.table(s.palette)
