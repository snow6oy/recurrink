import xml.etree.ElementTree as ET
import pprint
import math
#from recurrink import TmpFile
from db import Models, Blocks
pp = pprint.PrettyPrinter(indent = 2)

class Stencil:
  ''' accept a cell dictionary and for each unique colour
      create a new view as a black white negative
      return a set of views
  ''' 
  def __init__(self, model, data):
    self.model = model
    self.data = data # read-only copy for generating colmap

  def colours(self):
    ''' colour counter depends on shape
    '''
    seen = dict()
    keys = list()
    for cell in self.data:
      c = self.data[cell]
      fo = float(c['fill_opacity'])
      if fo >= 1:  # background is irrelevant when foreground is opaque
        if c['shape'] == 'square' or c['shape'] == 'circle' and c['size'] == 'large':
          keys.append(tuple([cell, self.composite(c['fill']), 'fill']))
        else:
          keys.append(tuple([cell, self.composite(c['fill']), 'fill']))
          keys.append(tuple([cell, self.composite(c['bg']), 'bg']))
      else:
        #name = self.composite(c['fill'], c['bg'], c['fill_opacity'])
        name = self.composite(c['fill'], c['bg'], fo)
        keys.append(tuple([cell, name, 'fill']))
        keys.append(tuple([cell, self.composite(c['bg']), 'bg']))
      if c['stroke_width']:
        #name = self.composite(c['stroke'], c['bg'], c['fill_opacity'])
        so = float(c['stroke_opacity'])
        name = self.composite(c['stroke'], c['bg'], so)
        keys.append(tuple([cell, name, 'stroke']))

    self.colmap = keys # helps build a stencil later
    for k in keys:
      uniqcol = k[1]
      if uniqcol in seen:
        seen[uniqcol] += 1 
      else:
        seen[uniqcol] = 1
    return list(seen.keys())
 
  def monochrome(self, colour, celldata): # send a copy
    ''' use the colmap to return a view with black areas where a colour matched
        everything else is white
    '''
    for cell in celldata:
      for area in ['fill', 'bg', 'stroke']:
        found = [cm[2] for cm in self.colmap if cm[0] == cell and cm[1] == colour and cm[2] == area]
        celldata[cell][area] = '#000' if len(found) else '#FFF'
        celldata[cell]['fill_opacity'] = celldata[cell]['stroke_opacity'] = 1
    return celldata

  def composite(self, fill, bg=None, fo=None):
    ''' dinky likkle method to make nice filenames
    '''
    fo = str(round(fo * 10)) if fo else '' # 0.7 > 7
    bg = bg[1:] if bg else '' # remove the leading #
    fn = ''.join([fill[1:], bg[1:], fo])
    return fn.lower()

class Points:
  ''' nw n ne    do the maths to render a cell
      w  c  e    points are calculated and called as p.ne p.nne p.s
      sw s se
  '''
  def __init__(self, x, y, stroke_width, size):
    self.n  = [x + size / 2,              y + stroke_width]
    self.e  = [x + size - stroke_width,   y + size / 2]
    self.s  = [x + size / 2,              y + size - stroke_width]
    self.w  = [x + stroke_width,          y + size / 2]
    self.ne = [x + size - stroke_width,   y + stroke_width] 
    self.se = [x + size - stroke_width,   y + size - stroke_width]
    self.nw = [x + stroke_width,          y + stroke_width]
    self.sw = [x + stroke_width,          y + size - stroke_width]
    self.mid= [x + size / 2,              y + size / 2]

class Svg:
  def __init__(self, scale, cellsize):
    ns = '{http://www.w3.org/2000/svg}'
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      xmlns:svg="http://www.w3.org/2000/svg" 
      viewBox="0 0 1080 1080" width="1080px" height="1080px"
      transform="scale({scale})"></svg>
    ''')
    #ET.dump(root)
    self.ns = ns
    self.root = root
    self.cellsize = cellsize

  def group(self, gid):
    return ET.SubElement(self.root, f"{self.ns}g", id=gid)

  def foreground(self, x, y, sid, cell, g):
    ''' create a shape from a cell for adding to a group
    '''
    facing = cell['facing']
    shape = cell['shape']
    size = cell['size']
    hsw = cell['stroke_width'] / 2  
    sw = cell['stroke_width']
    p = Points(x, y, sw, self.cellsize)

    if shape == 'circle':
      self.circle(sid, size, sw, p, g)
    elif shape == 'line':
      self.line(x, y, sid, facing, size, hsw, sw, g)
    elif shape == 'square':
      self.square(x, y, sid, size, hsw, sw, g)
    elif shape == 'triangl':
      self.triangle(sid, facing, p, g)
    elif shape == 'diamond':
      self.diamond(sid, facing, p, g)
    else:
      self.default(x, y, sid, shape, g)
  
  def circle(self, sid, size, stroke_width, p, g):
    cs = self.cellsize
    if size == 'large': 
      cs /= 2
      sum_two_sides = (cs**2 + cs**2) # pythagoras was a pythonista :)
      r = math.sqrt(sum_two_sides) - stroke_width
    elif size == 'medium':
      r = (cs / 2 - stroke_width) # normal cs
    elif size == 'small':
      r = (cs / 3 - stroke_width) 
    else:
      raise ValueError(f"Cannot set circle to {size} size")
    circle = ET.SubElement(g, f"{self.ns}circle", id=sid)
    circle.set('cx', str(p.mid[0]))
    circle.set('cy', str(p.mid[1]))
    circle.set('r', str(r))


  def line(self, x, y, sid, facing, size, hsw, sw, g):
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    cs = self.cellsize
    facing = 'north' if facing == 'south' else facing
    facing = 'east' if facing == 'west' else facing
    if size == 'large' and facing == 'north':
      x      = str(x + cs / 3 + hsw)
      y      = str(y - cs / 3 + hsw)
      width  = str(cs / 3 - sw)
      height = str((cs / 3 * 2 + cs) - sw)
    elif size == 'large' and facing == 'east':
      x      = str(x - cs / 3 + hsw)
      y      = str(y + cs / 3 + hsw)
      width  = str((cs / 3 * 2 + cs) - sw)
      height = str(cs / 3 - sw)
    elif size == 'medium' and facing == 'north':
      x      = str(x + cs / 3 + hsw)
      y      = str(y + hsw)
      width  = str(cs / 3 - sw)
      height = str(cs - sw)
    elif size == 'medium' and facing == 'east':
      x      = str(x + hsw)
      y      = str(y + cs / 3 + hsw)
      width  = str(cs - sw)
      height = str(cs / 3 - sw)
    elif size == 'small' and facing == 'north':
      x      = str(x + cs / 3 + hsw)
      y      = str(y + cs / 4 + hsw)
      width  = str(cs / 3 - sw)
      height = str(cs / 2 - sw)
    elif size == 'small' and facing == 'east':
      x      = str(x + cs / 4 + hsw)
      y      = str(y + cs / 3 + hsw)
      width  = str(cs / 2 - sw)
      height = str(cs / 3 - sw)
    else:
      raise ValueError(f"Cannot set line to {size} {facing}")
    rect = ET.SubElement(g, f"{self.ns}rect", id=sid)
    rect.set("x", str(x))
    rect.set("y", str(y))
    rect.set("width", width)
    rect.set("height", height)

  def square(self, x, y, sid, size, hsw, sw, g):
    cs = self.cellsize
    if size == 'medium':
      x      = str(x + hsw)
      y      = str(y + hsw)
      width  = str(cs - sw)
      height = str(cs - sw)
    elif size == 'large':
      third  = cs / 3
      x      = str(x - third / 2 + hsw)
      y      = str(y - third / 2 + hsw)
      width  = str(cs + third - sw)
      height = str(cs + third - sw)
    elif size == 'small':
      third  = cs / 3
      x      = str(x + sw + third)
      y      = str(y + sw + third)
      width  = str(third - sw)
      height = str(third - sw)
    else:
      raise ValueError(f"Cannot make square with {size}")
    rect = ET.SubElement(g, f"{self.ns}rect", id=sid)
    rect.set("x", str(x))
    rect.set("y", str(y))
    rect.set("width", width)
    rect.set("height", height)

  def diamond(self, sid, facing, p, g):
    if facing == 'all': 
      points = p.w + p.n + p.e + p.s + p.w
    elif facing == 'west': 
      points = p.w + p.n + p.s + p.w
    elif facing == 'east': 
      points = p.n + p.e + p.s + p.n
    elif facing == 'north': 
      points = p.w + p.n + p.e + p.w
    elif facing == 'south':
      points = p.w + p.e + p.s + p.w
    else:
      raise ValueError(f"Cannot face diamond {facing}")
    polyg = ET.SubElement(g, f"{self.ns}polygon", id=sid)
    polyg.set("points", ','.join(map(str, points)))

  def triangle(self, sid, facing, p, g):
    if facing == 'west': 
      points = p.w + p.ne + p.se + p.w
    elif facing == 'east': 
      points = p.nw + p.e + p.sw + p.nw
    elif facing == 'north': 
      points = p.sw + p.n + p.se + p.sw
    elif facing == 'south':
      points = p.nw + p.ne + p.s + p.nw
    else:
      raise ValueError(f"Cannot face triangle {facing}")
    polyg = ET.SubElement(g, f"{self.ns}polygon", id=sid)
    polyg.set("points", ','.join(map(str, points)))

  def default(self, x, y, sid, words, g):
    t = ET.SubElement(g, f"{self.ns}text", id=sid)
    t.text = words
    tx = x + 10
    ty = y + 30
    t.set("x", str(tx))
    t.set("y", str(ty))
    t.set("class", "{fill:#000;fill-opacity:1.0}")

  def write(self, svgfile):
    tree = ET.ElementTree(self.root)
    tree.write(svgfile)

class Layout(Svg):
  ''' expand cells provided by Draw across a canvas
  '''
  def __init__(self, scale=1.0):
    ''' scale expected to be one of [0.5, 1.0, 1.5, 2.0]
        in another universe they would all be integers 1 2 3 4
    '''
    self.scale = scale
    #self.cellsize = round(60 / scale)
    self.cellsize = 60
    self.grid = round(1080 / (60 * scale))
    if False: # run with scale 0.5 to get a demo
      for col in range(self.grid):
        for row in range(self.grid):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()
    super().__init__(scale, self.cellsize)

  def style(self, c, cell):
    ''' makes an svg group for each style
    '''
    bg = self.group(f"{c}0") # draw background  cells
    bg.set("style", f"fill:{cell['bg']};stroke-width:0") # hide the cracks between the background tiles
    fg = self.group(f"{c}1") # draw foreground cells
    fg.set("style", f"fill:{cell['fill']};fill-opacity:{cell['fill_opacity']};stroke:{cell['stroke']};" +
      f"stroke-width:{cell['stroke_width']};stroke-dasharray:{cell['stroke_dasharray']};" +
      f"stroke-opacity:{cell['stroke_opacity']}"
    )
    return bg, fg

  def gridwalk(self, blocksize, positions, cells):
    ''' traverse the grid once for each block
    '''
    for c in cells: # top cells must be last
      print(c, end=' ',flush=True) 
      cell = cells[c]
      bg, fg = self.style(c, cell)
      for y in range(0, self.grid, blocksize[1]):
        for x in range(0, self.grid, blocksize[0]):
          grid = tuple([x, y])
          self.renderblock(grid, blocksize, positions, c, cell, bg, fg)
    print()

  def renderblock(self, grid, blocksize, positions, c, cell, bg, fg):
    ''' scan a block, match cell to position
    '''
    for y in range(blocksize[1]):
      for x in range(blocksize[0]):
        pos = tuple([x, y])
        ct = positions[pos] # cell, top
        c0 = ct[0] if type(ct) is tuple else ct
        c1 = ct[1] if type(ct) is tuple else None
        if c == c0:
          self.rendercell(grid, x, y, c0, c1, cell, bg, fg)
    return None

  def rendercell(self, grid, x, y, c0, c1, cell, bg, fg):
    ''' render a cell by adding shape elements to the style group
    '''
    X = (grid[0] + x) * self.cellsize # this logic is the base for Points
    Y = (grid[1] + y) * self.cellsize
    #print(grid, X, Y, c0, c1, cell['shape'])
    self.square(X, Y, f"{c0}0-{x}-{y}", 'medium', 0, 0, bg) 
    if cell['top']:
      self.foreground(X, Y, f"{c1}1-{x}-{y}", cell, fg) 
    if ord(c0) < 97:  # upper case
      cell['shape'] = ' '.join([c0, cell['shape']])
    self.foreground(X, Y, f"{c0}1-{x}-{y}", cell, fg) 

if __name__ == '__main__':
  #tf = TmpFile()
  model = 'mambo'
  m = Models()
  blocksize = m.read(model=model)[2] # can get scale too
  b = Blocks(model)
  positions = b.read()
  #pp.pprint(blocksize)
  #pp.pprint(positions)
  s = 1.5
  lt = Layout(scale=s)
  #print(f"s {lt.scale} c {lt.cellsize} g {lt.grid}")
  #cells = lt.testdata()
  cells = tf.read(model, output=dict())
  lt.gridwalk(blocksize, positions, cells)
  lt.write(model)
