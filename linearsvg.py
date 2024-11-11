from config import *
import xml.etree.ElementTree as ET
from outfile import Svg
from flatten import Rectangle, Flatten
import pprint
pp = pprint.PrettyPrinter(indent=2)

'''
    [(0, 0, 3, 3), 'CCC'],
    [(3, 0, 3, 3), 'CCC'],
    [(6, 0, 3, 3), 'CCC'],
    [(0, 0, 3, 3), 'FFF'],
    [(4, 0, 1, 3), '000'],
    [(7, 1, 1, 1), '000'],
    [(1, 1, 1, 1), '000'],
    [(2, 1, 5, 1), 'FFF'] 
'''
#[print(c) for c in config.cells]

class LinearSvg(Svg):
  ''' output design to a two dimensional SVG that a plotter can understand
  '''
  def __init__(self, scale, gridsize=None, cellsize=None):
    if gridsize and cellsize:
      super().__init__(unit='mm', scale=scale, gridsize=gridsize, cellsize=cellsize)
    else:
      super().__init__(unit='mm', scale=scale)
 
  def blockify(self):
    ''' pack the cells back into their blocks
        preserve top order
    '''
    block_x, block_y = self.blocksize
    total_x = int(block_x * self.cellsize)
    total_y = int(block_y * self.cellsize)
    grid_mm = int(self.cellnum * self.cellsize)
    blocks = []
    print(f"{self.blocksize=} {self.cellnum=} {grid_mm=} {self.cellsize=} {total_x=} {total_y=}")

    for x in range(0, grid_mm, total_x):
      for y in range(0, grid_mm, total_y):
        shapes = []
        min_x  = x
        max_x  = x + total_x
        min_y  = y
        max_y  = y + total_y
        #print(f"{min_x=} {max_x=} {min_y=} {max_y=}")
        for d in self.doc:
          for shape in d['shapes']:
            X, Y = shape['x'], shape['y']
            if X >= min_x and X < max_x and Y >= min_y and Y < max_y:
              #print(tuple([X, Y]))
              shape['style'] = self.trimStyle(d['style']) # trim style from parent
              shapes.append(shape)
        blocks.append(shapes)
    return blocks

  def regroupColors(self, done):
    self.doc = dict()     # reset
    for d in done:
      d.meander(gap=1)
      xy = list(d.linefill.coords)
      ''' the culprits!
      if d.label == 'R000    12  6 15  9' or d.label == 'R000    12  0 15  3':
        print(f"{d.label=} {d.pencolor=}")
        pp.pprint(xy)
        xy = []
      '''
      if d.pencolor in self.doc:
        self.doc[d.pencolor].append(xy)
      else:
        self.doc[d.pencolor] = list()
        self.doc[d.pencolor].append(xy)

  def _makeRectangles(self):
    ''' convert all cells made by Layer() into Rectangle objects
    '''
    rectangles = list()

    for group in self.doc:
      for cell in group['shapes']:
        style = group['style']  # each group has a uniq style
        x, y = tuple([round(float(cell['x'])), round(float(cell['y']))])
        w, h = tuple([round(float(cell['width'])), round(float(cell['height']))])
        r = Rectangle(pencolor=self.trimStyle(group['style']), x=x, y=y, w=w, h=h)
        rectangles.append(r)
        #print(cell['x'], r.label)
    return list(reversed(rectangles))  # top cells are done first

  def makeRectangles(self, block):
    ''' convert cells from blockify into Rectangle objects
    '''
    rectangles = list()

    for cell in block:
      fill = cell['style']  # e.g. FFF
      x, y = tuple([round(float(cell['x'])), round(float(cell['y']))])
      w, h = tuple([round(float(cell['width'])), round(float(cell['height']))])
      r = Rectangle(pencolor=fill, x=x, y=y, w=w, h=h)
      rectangles.append(r)
      #print(cell['x'], r.label)
    return list(reversed(rectangles))  # top cells are done first

  def make(self):
    ''' orchestrate the transformation of incoming cells into SVG lines
    '''
    for block in self.blockify():
      todo = self.makeRectangles(block)
      f = Flatten()
      done = f.run(todo)
      #[print(r.label) for r in done]
      ''' now that Flatten.done contains two-d cells sort them for SVG layers
          and create SVG elements
      '''
      self.regroupColors(done)
      #pp.pprint(self.doc)
      #pp.pprint(self.doc['FFF'][0])
      self.svgGroup()

  def svgGroup(self):
    uniqid = 0
    for pencolor in self.doc:
      #pencolor = '00C' if pencolor == 'FFF' else pencolor # plotting on white paper
      #if pencolor in ['CCC','000']: break
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', f"fill:none;stroke:#{pencolor}")

      for coords in self.doc[pencolor]:
        uniqid += 1
        points = str()
        for c in coords:
          x = c[0]
          y = c[1]
          points += f"{x},{y} "
        polyln = ET.SubElement(g, f"{self.ns}polyline", id=str(uniqid))
        polyln.set("points", points)

gs  = 270
cs  = 54
#svg = LinearSvg(scale=.5, gridsize=gs, cellsize=cs)
svg = LinearSvg(scale=2)
blocksize = (3, 1)
svg.gridwalk(blocksize, config.positions, config.cells)
svg.make()
svg.write('/tmp/minkscape.svg')
'''
the
end
'''
