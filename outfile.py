import math
import pprint
import xml.etree.ElementTree as ET
from gcwriter import GcodeWriter
pp = pprint.PrettyPrinter(indent = 2)

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

class Shapes():

  def foreground(self, x, y, cell, g):
    ''' create a shape from a cell for adding to a group
    '''
    facing = cell['facing']
    shape = cell['shape']
    size = cell['size']
    hsw = cell['stroke_width'] / 2
    sw = cell['stroke_width']
    p = Points(x, y, sw, self.cellsize)

    if shape == 'circle':
      self.circle(size, sw, p, g)
    elif shape == 'square':
      self.square(x, y, size, hsw, sw, g)
    elif shape == 'line':
      self.line(x, y, facing, size, hsw, sw, g)
    elif shape == 'triangl':
      self.triangle(facing, p, g)
    elif shape == 'diamond':
      self.diamond(facing, p, g)
    else:
      print(f"Warning: do not know {shape}")
      self.text(shape, x, y, g)

  def circle(self, size, stroke_width, p, g):
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
    g.append({
      'name': 'circle', 'cx': str(p.mid[0]), 'cy': str(p.mid[1]), 'r': str(r)
    })

  def square(self, x, y, size, hsw, sw, g):
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
    g.append({
      'name': 'rect', 'x': x, 'y': y, 'width': width, 'height': height
    })

  def line(self, x, y, facing, size, hsw, sw, g):
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
    g.append({
      'name': 'rect', 'x': x, 'y': y, 'width': width, 'height': height
    })

  def triangle(self, facing, p, g):
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
    g.append({
      'name': 'polygon', 
      'points': ','.join(map(str, points))
    })

  def diamond(self, facing, p, g):
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
    g.append({
      'name': 'polygon', 
      'points': ','.join(map(str, points))
    })

  def text(self, name, x, y, g):
    g.append({ 'name': name, 'x': x, 'y': y })

class Layout(Shapes):
  ''' expand cells and draw across grid
     9 * 60 = 540  * 2.0 = 1080
    12 * 60 = 720  * 1.5 = 1080
    18 * 60 = 1080 * 1.0 = 1080
    36 * 60 = 2160 * 0.5 = 1080

    return celldata in a layout for output as either SVG or Gcode
    { "width":"180px", "height":"180px", "scale": 1,
      "groups": [{
        "fill":"#CCC",
        "stroke-width":0,
        "shapes": [
          { "x": 0, "y": 0, "width": 60, "height": 60 } ]} ] }
    '''

  def __init__(self, scale=1.0, gridpx=1080, cellsize=60):
    ''' scale expected to be one of [0.5, 1.0, 1.5, 2.0]
    '''
    self.scale = scale
    self.grid = round(gridpx / (cellsize * scale))
    self.cellsize = round(cellsize * scale)
    self.styles = dict() # unique style associated with many cells
    self.seen = str()    # have we seen this style before
    if False:            # run with gridpx=180 to get a demo
      for col in range(self.grid):
        for row in range(self.grid):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()
    self.doc = list()
    #self.doc['scale'] = scale
    #self.doc['height'] = self.doc['width'] = gridpx
    #self.doc['groups'] = list()

  def gridwalk(self, blocksize, positions, cells):
    ''' traverse the grid once for each block, populating ET elems as we go
    '''
    self.cells = cells
    for layer in ['bg', 'fg', 'top']:
      for cell in self.cells:
        self.uniqstyle(cell, layer, self.cells[cell]['top'],
          bg=self.cells[cell]['bg'],
          fill=self.cells[cell]['fill'],
          fo=self.cells[cell]['fill_opacity'],
          stroke=self.cells[cell]['stroke'],
          sd=self.cells[cell]['stroke_dasharray'],
          so=self.cells[cell]['stroke_opacity'],
          sw=self.cells[cell]['stroke_width']
        )
      for cell in self.cells:
        for gy in range(0, self.grid, blocksize[1]):
          for gx in range(0, self.grid, blocksize[0]):
            for y in range(blocksize[1]):
              for x in range(blocksize[0]):
                pos = tuple([x, y])
                c, t = positions[pos] # cell, top
                self.rendercell(layer, cell, c, t, gx, x, gy, y)
      self.styles.clear() # empty self.styles before next layer


  def getgroup(self, layer, cell):
    ''' combine style and counter to make a group
    '''
    style = self.findstyle(cell) 
    if style != self.seen:
      self.seen = style # HINT use python set() instead of self.seen
      self.doc.append({ 'style': style, 'shapes': list() })
    return self.doc[-1]['shapes']

  def rendercell(self, layer, cell, c, t, gx, x, gy, y):
    ''' gather inputs call Shapes() and add shape to group
    '''
    X = (gx + x) * self.cellsize # this logic is the base for Points
    Y = (gy + y) * self.cellsize
    if layer == 'bg' and cell == c:
      g = self.getgroup('bg', cell)
      self.square(X, Y, 'medium', 0, 0, g) 
    if layer == 'fg' and cell == c:
      if ord(cell) < 97:  # upper case
        self.cells[cell]['shape'] = ' '.join([c, self.cells[cell]['shape']]) # testcard hack
      g = self.getgroup('fg', cell)
      self.foreground(X, Y, self.cells[cell], g) 
    if layer == 'top' and cell == t and self.cells[cell]['top']:
      g = self.getgroup('top', cell)
      self.foreground(X, Y, self.cells[cell], g) 

  def uniqstyle(self, cell, layer, top, bg=None, fill=None, fo=None, stroke=None, sw=None, sd=None, so=None):
    ''' remember what style to use for this cell and that layer
    '''
    style = str()
    if layer == 'bg': # create new entry in self.layers.bg
      style = f"fill:{bg};stroke-width:0" # hide the cracks between the background tiles
    elif layer == 'fg' and sw: # and not top:
      style = f"fill:{fill};fill-opacity:{fo};stroke:{stroke};stroke-width:{sw};stroke-dasharray:{sd};stroke-opacity:{so}"
    elif layer == 'fg': # and not top:
      style = f"fill:{fill};fill-opacity:{fo}"
    elif layer == 'top' and top and sw:
      style = f"fill:{fill};fill-opacity:{fo};stroke:{stroke};stroke-width:{sw};stroke-dasharray:{sd};stroke-opacity:{so}"
    elif layer == 'top' and top:
      style = f"fill:{fill};fill-opacity:{fo}"

    if style and style in self.styles:
      self.styles[style].append(cell)
    elif style:
      self.styles[style] = list()
      self.styles[style].append(cell)

  def findstyle(self, cell):
    ''' find a style saved in uniqstyle
    '''
    found = None
    for s in self.styles:
      if cell in self.styles[s]:
        found = s
        break
    if not found: 
      raise ValueError(f"{cell} aint got no style (hint: cannot make bg for topcell?)")
    return found

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

class Svg(Layout):
  def __init__(self, scale, gridpx=1080, cellsize=60):
    # svg:transform(scale) does the same but is lost when converting to raster. Instagram !!!
    ns = '{http://www.w3.org/2000/svg}'
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      xmlns:svg="http://www.w3.org/2000/svg" 
      viewBox="0 0 {gridpx} {gridpx}" width="{gridpx}px" height="{gridpx}px"
      transform="scale(1)"></svg>
    ''')
    comment = ET.Comment(f' scale:{scale} cellpx:{cellsize} ')
    root.insert(0, comment)  # 0 is the index where comment is inserted
    #ET.dump(root)
    self.ns = ns
    self.root = root
    super().__init__(scale, gridpx, cellsize)

  def make(self):
    ''' expand the doc from gridwalk and convert to XML
    '''
    uniqid = 0 # xml elements must have unique IDs
    for group in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', group['style'])
      for s in group['shapes']:
        uniqid += 1
        name = s['name']
        #print(name, str(uniqid))
        if name == 'circle':
          circle = ET.SubElement(g, f"{self.ns}circle", id=str(uniqid))
          circle.set('cx', s['cx'])
          circle.set('cy', s['cy'])
          circle.set('r', s['r'])
        elif name == 'rect':
          rect = ET.SubElement(g, f"{self.ns}rect", id=str(uniqid))
          rect.set("x", s['x'])
          rect.set("y", s['y'])
          rect.set("width", s['width'])
          rect.set("height", s['height'])
        elif name == 'polygon':
          polyg = ET.SubElement(g, f"{self.ns}polygon", id=str(uniqid))
          polyg.set("points", s['points'])
        else:
          t = ET.SubElement(g, f"{self.ns}text", id=str(uniqid))
          t.text = name
          tx = s['x'] + 10
          ty = s['y'] + 30
          t.set("x", str(tx))
          t.set("y", str(ty))
          t.set("class", "{fill:#000;fill-opacity:1.0}")

  def write(self, svgfile):
    tree = ET.ElementTree(self.root)
    ET.indent(tree, level=0)
    tree.write(svgfile)

# TODO instead of writing to file send gcode to USB
# https://github.com/jminardi/mecode?tab=readme-ov-file#direct-control-via-serial-communication
class Gcode(Layout):
  ''' Paper size is A4: 60px / 10 = 6mm
  '''
  def __init__(self, scale, gridpx, cellsize):
    self.gcdata = dict()
    self.cubesz = round(cellsize / 3)
    super().__init__(scale=scale, gridpx=gridpx, cellsize=cellsize)

  def make(self):
    for group in self.doc:
      fill = None
      for pencol in ['fill:#CCC', 'fill:#FFF', 'fill:#000']:
        if pencol in group['style']:
          fill = pencol
      for cell in group['shapes']:
        self.cube(cell, fill)

  def write(self, model, fill='fill:#FFF'):
    ''' stream path data to file as gcodes
    '''
    gcw = GcodeWriter()
    fillname = fill.split('#')[1]
    fn = f'/tmp/{model}_{fillname}.gcode'
    gcw.writer(fn)
    gcw.start()
    for startpos in self.gcdata:
      if self.gcdata[startpos] == fill:
        cube = [startpos]
        cube.append(tuple([startpos[0], startpos[1] + self.cubesz]))
        cube.append(tuple([startpos[0] + self.cubesz, startpos[1] + self.cubesz]))
        cube.append(tuple([startpos[0] + self.cubesz, startpos[1]]))
        cube.append(startpos)
        gcw.points(cube)
    gcw.stop()
    return fn

  def cube(self, cell, fill):
    ''' Slice a cell into nine cubes, each 20x20
        Example: cube({'name': 'rect', 'x': '120', 'y': '120', 'width': '60', 'height': '60'})
    '''
    x = round(float(cell['x'])) # TODO ask Layout to send integers
    y = round(float(cell['y']))
    w = round(float(cell['width']))
    h = round(float(cell['height']))
    for Y in range(y, (h + y), self.cubesz):
      for X in range(x, (w + x), self.cubesz):
        moveto = tuple([X, Y])
        self.gcdata[moveto] = fill # top overwrites fg which overwrites bg


if __name__ == '__main__':
  positions = { 
    (0, 0): ('a', 'c'),  # c is both cell and top
    (1, 0): ('b', 'd'),  # d is only top
    (2, 0): ('c',None)
  }
  cells = {
    'a': {
      'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
      'shape': 'square', 'facing': 'all', 'size': 'medium', 'top': False,
      'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    },
    'b': {
      'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
      'shape': 'line', 'facing': 'north', 'size': 'medium', 'top': False,
      'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    },
    'c': {
      'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
      'shape': 'square', 'facing': 'all', 'size': 'small', 'top': True,
      'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 1.0, 'stroke_width': 0, 
    },
    'd': {
      'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
      'shape': 'line', 'facing': 'east', 'size': 'large', 'top': True,
      'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    }
  }
  '''
  '''
  if False:
    svg = Svg(scale=1.0, gridpx=180) # 180px / 60px = 3 cells high and 3 cells wide
    svg.gridwalk((3, 1), positions, cells)
    svg.make()
    #pp.pprint(svg.doc)
    svg.write('/tmp/minkscape.svg')
  else:
    gc = Gcode(scale=1.0, gridpx=6, cellsize=6)
    gc.gridwalk((3, 1), positions, cells)
    gc.make()
    #pp.pprint(gc.gcdata)
    print(gc.write('minkscape', fill='fill:#CCC'))
  '''
  the
  end
  '''
