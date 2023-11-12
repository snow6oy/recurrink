import xml.etree.ElementTree as ET
import pprint
from db import Styles
pp = pprint.PrettyPrinter(indent = 2)

class Palette:
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

if __name__ == '__main__':
  s = Styles()
  # ver='htmstarter'
  ver='colour45'
  s.set_spectrum(ver=ver)
  #xml = Palette(300, 60)
  xml = Palette(540, 300)
  #pp.pprint(s.palette)
  xml.make(s.palette)
  xml.write(ver)
  xml.table(s.palette)
