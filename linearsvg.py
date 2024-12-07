from config import *
import xml.etree.ElementTree as ET
from outfile import Svg
from flatten import Rectangle, Flatten
import pprint
pp = pprint.PrettyPrinter(indent=2)

class LinearSvg(Svg):
  ''' output design to a two dimensional SVG that a plotter can understand
  '''
  def __init__(self, scale, gridsize=None, cellsize=None):
    if gridsize and cellsize:
      super().__init__(unit='mm', scale=scale, gridsize=gridsize, cellsize=cellsize)
    else:
      super().__init__(unit='mm', scale=scale)

  def make(self):
    ''' orchestrate the transformation of incoming cells into SVG lines
    '''
    blocks   = self.blockify()
    self.doc = dict()     # reset for regrouping by fill
    for block in blocks:
      todo = self.makeRectangles(block)
      f = Flatten()
      done = f.run(todo)
      self.regroupColors(done)
    ''' now that Flatten.done contains two-d cells sort them for SVG layers
        and create SVG elements
    '''
    self.svgGroup()
 
  def blockify(self):
    ''' pack the cells back into their blocks
        preserve top order
    '''
    block_x, block_y = self.blocksize
    total_x = int(block_x * self.cellsize)
    total_y = int(block_y * self.cellsize)
    grid_mm = int(self.cellnum * self.cellsize)
    blocks = []
    #print(f"{self.blocksize=} {self.cellnum=} {grid_mm=} {self.cellsize=} {total_x=} {total_y=}")

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
    for d in done:
      d.meander()
      xy = list(d.linefill.coords)
      if d.pencolor in self.doc:
        self.doc[d.pencolor].append(xy)
      else:
        self.doc[d.pencolor] = list()
        self.doc[d.pencolor].append(xy)

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

svg = LinearSvg(scale=2)
blocksize = (3, 1)
svg.gridwalk(blocksize, config.positions, config.cells)
svg.make()
svg.write('tmp/minkscape_2.svg')
'''
the
end
'''
