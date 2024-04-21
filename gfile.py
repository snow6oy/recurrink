import xml.etree.ElementTree as ET
import pprint
#from mecode import G
from gcwriter import GcodeWriter
pp = pprint.PrettyPrinter(indent = 2)

class Shapes():

  def foreground(self, x, y, cell, g):
    ''' create a shape from a cell for adding to a group
    '''
    facing = cell['facing']
    shape = cell['shape']
    size = cell['size']
    hsw = cell['stroke_width'] / 2
    sw = cell['stroke_width']
    #p = Points(x, y, sw, self.cellsize)

    if shape == 'square':
      self.square(x, y, size, hsw, sw, g)
    elif shape == 'line':
      self.line(x, y, facing, size, hsw, sw, g)
    else:
      print(f"unknown {shape}")

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
    ''' gather inputs and call Svg()
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
        #print(s['name'], s['x'], s['y'], s['width'], s['height'], str(uniqid) )
        name, x, y, w, h = s['name'], s['x'], s['y'], s['width'], s['height']
        shape = ET.SubElement(g, f"{self.ns}{name}", id=str(uniqid))
        if name == 'rect':
          shape.set("x", x)
          shape.set("y", y)
          shape.set("width", w)
          shape.set("height", h)
        # TODO add more shapes here

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
