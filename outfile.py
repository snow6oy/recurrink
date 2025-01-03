import math
import pprint
import xml.etree.ElementTree as ET
from shapes import Geomink # Rectangle #, Flatten
from flatten import Flatten
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

  #def foreground(self, x, y, cell, g):
  def foreground(self, x, y, cell):
    ''' create a shape from a cell for adding to a group
  
        fix for update --mm is to ignore stroke whenever it causes width to be less than one
    '''
    facing = cell['facing']
    shape = cell['shape']
    size = cell['size']
    hsw = (cell['stroke_width'] / 2) * self.scale
    sw = cell['stroke_width'] * self.scale
    p = Points(x, y, sw, self.cellsize)
    #print(f"cell size:{self.cellsize} shape size:{size} shape:{shape} x:{x} y:{y} half stroke width:{hsw} stroke width:{sw}")
    if shape == 'circle':
      s = self.circle(size, sw, p)
    elif shape == 'square':
      s = self.square(x, y, size, hsw, sw)
      if s['width'] < 1 or s['height'] < 1:
        s = self.square(x, y, size, hsw, 0)
    elif shape == 'line':
      s = self.line(x, y, facing, size, hsw, sw)
      if s['width'] < 1 or s['height'] < 1:
        s = self.line(x, y, facing, size, hsw, 0)
    elif shape == 'triangl':
      s = self.triangle(facing, p)
    elif shape == 'diamond':
      s = self.diamond(facing, p)
    else:
      print(f"Warning: do not know {shape}")
      s = self.text(shape, x, y)

    if 'width' in s and s['width'] < 1:
      raise ValueError(f"square too small width: {s['width']} orig {cell['width']}")
    elif 'height' in s and s['height'] < 1:
      raise ValueError(f"square too small height: {s['height']}")
    s['name'] = shape
    return s

  def circle(self, size, stroke_width, p):
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
    return { 'cx': p.mid[0], 'cy': p.mid[1], 'r': r }

  def square(self, x, y, size, hsw, sw):
    cs = self.cellsize
    if size == 'medium':
      x      = (x + hsw)
      y      = (y + hsw)
      width  = (cs - sw)
      height = (cs - sw)
    elif size == 'large':
      third  = cs / 3
      x      = (x - third / 2 + hsw)
      y      = (y - third / 2 + hsw)
      width  = (cs + third - sw)
      height = (cs + third - sw)
    elif size == 'small':
      third  = cs / 3
      x      = (x + third + hsw)
      y      = (y + third + hsw)
      width  = (third - sw)
      height = (third - sw)
    else:
      raise ValueError(f"Cannot make square with {size}")
    return { 'x': x, 'y': y, 'width': width, 'height': height }

  def line(self, x, y, facing, size, hsw, sw):
    ''' lines can be orientated along a north-south axis or east-west axis
        but the user can choose any of the four cardinal directions
        here we silently collapse the non-sensical directions
    '''
    cs = self.cellsize
    facing = 'north' if facing == 'south' else facing
    facing = 'east' if facing == 'west' else facing
    if size == 'large' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y - cs / 3 + hsw)
      width  = (cs / 3 - sw)
      height = ((cs / 3 * 2 + cs) - sw)
    elif size == 'large' and facing == 'east':
      x      = (x - cs / 3 + hsw)
      y      = (y + cs / 3 + hsw)
      width  = ((cs / 3 * 2 + cs) - sw)
      height = (cs / 3 - sw)
    elif size == 'medium' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y + hsw)
      width  = cs / 3 - sw
      height = (cs - sw)
    elif size == 'medium' and facing == 'east':
      x      = (x + hsw)
      y      = (y + cs / 3 + hsw)
      width  = (cs - sw)
      height = (cs / 3 - sw)
    elif size == 'small' and facing == 'north':
      x      = (x + cs / 3 + hsw)
      y      = (y + cs / 4 + hsw)
      width  = (cs / 3 - sw)
      height = (cs / 2 - sw)
    elif size == 'small' and facing == 'east':
      x      = (x + cs / 4 + hsw)
      y      = (y + cs / 3 + hsw)
      width  = (cs / 2 - sw)
      height = (cs / 3 - sw)
    else:
      raise ValueError(f"Cannot set line to {size} {facing}")
    return { 'x': x, 'y': y, 'width': width, 'height': height }

  def triangle(self, facing, p):
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
    return { 'points': ','.join(map(str, points)) }

  def diamond(self, facing, p):
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
    return { 'points': ','.join(map(str, points)) }

  def text(self, name, x, y):
    return { 'x': x, 'y': y }

class Layout(Shapes):
  ''' the below cell sizes were calculated as
      gridsize / scale / cellnum
      18 was chosen as the preferred number of cells
      for both column and row with scale 1
      the num of cells is gridsize / cellsize

        PIXELS

        num of  cell           grid
         cells  size   scale   size
        ---------------------------------
             9 *  120    * 2.0 = 1080
            12 *   90    * 1.5 = 1080
            18 *   60    * 1.0 = 1080
            24 *   45    * .75 = 1080
            36 *   30    * 0.5 = 1080

        MILLIMETERS

             9 *   30    * 2.0 =  270
            18 *   15    * 1.0 =  270 
            36 *    9    * 0.6 =  270
  '''
  def __init__(self, unit='px', scale=1.0, gridsize=None, cellsize=None):

    self.governance = {
      'mm': { 'gridsize':270,  'cellsize':15, 'scale': [0.6, 1.0, 2.0] },
      'px': { 'gridsize':1080, 'cellsize':60, 'scale': [0.5, 0.75, 1.0, 1.5, 2.0] }
    }
    msg = self.checksum(unit, scale, cellsize)
    if msg:
      raise ValueError(msg)
    gridsize      = gridsize if gridsize else self.governance[unit]['gridsize']   
    cellsize      = cellsize if cellsize else self.governance[unit]['cellsize']
    self.unit     = unit
    self.scale    = float(scale)
    self.cellnum  = round(gridsize / (cellsize * scale))
    self.cellsize = round(cellsize * scale)
    self.gridsize = gridsize
    self.styles   = dict() # unique style associated with many cells
    self.seen     = str()    # have we seen this style before
    self.doc      = list()
    if False:           # run with gridsize=60 cellsize=6 to get a demo
      for col in range(self.cellnum):
        for row in range(self.cellnum):
          xy = tuple([row, col])
          print(xy, end=' ', flush=True)
        print()

  def gridwalk(self, blocksize, positions, cells):
    ''' traverse the grid once for each block, populating ET elems as we go
    '''
    self.cells = cells
    self.blocksize = blocksize         # pass blocksize to LinearSvg()
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
        for gy in range(0, self.cellnum, blocksize[1]):
          for gx in range(0, self.cellnum, blocksize[0]):
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
      bgcell = { 'facing': 'all', 'shape': 'square', 'size': 'medium', 'stroke_width': 0 }
      g.append(self.foreground(X, Y, bgcell))
    if layer == 'fg' and cell == c:
      if ord(cell) < 97:  # upper case
        self.cells[cell]['shape'] = ' '.join([c, self.cells[cell]['shape']]) # testcard hack
      g = self.getgroup('fg', cell)
      g.append(self.foreground(X, Y, self.cells[cell]))
    if layer == 'top' and cell == t and self.cells[cell]['top']:
      g = self.getgroup('top', cell)
      g.append(self.foreground(X, Y, self.cells[cell]))

  def uniqstyle(self, cell, layer, top, bg=None, fill=None, fo=1, stroke=None, sw=0, sd=0, so=1):
    ''' remember what style to use for this cell and that layer
        as None is invalid XML we use 0 as default for: fo sw sd so
    '''
    if bg is None and fill is None:
      raise ValueError(f"either {bg} or {fill} are empty")
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

  def checksum(self, unit, scale, cellsize):
    ''' sanity check the inputs
    '''
    if unit not in list(self.governance.keys()):
      return f'checksum failed: unknown unit {unit}'
    elif scale not in self.governance[unit]['scale']: # scale must in range
      return f'checksum failed scale {scale}'
    elif cellsize and (cellsize % 3):                 # cellsize / 3 must be a whole number
      return f'checksum failed cell size div by three {cellsize}'
    else:
      return None

  def trimStyle(self, style):
    start = style.index('#') + 1
    end = style.index(';')
    return style[start:end]

class Svg(Layout):
  def __init__(self, scale=1, unit='px', gridsize=0, cellsize=0, inkscape=False):
    ''' svg:transform(scale) is better than homemade scaling
        but is lost when converting to raster. Instagram !!!
    '''
    super().__init__(unit, scale, gridsize, cellsize)
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 {self.gridsize} {self.gridsize}" 
      width="{self.gridsize}{self.unit}" height="{self.gridsize}{self.unit}"
      transform="scale(1)"></svg>
    ''')
    comment = ET.Comment(
      f' scale:{scale} cellsize:{cellsize} gridsize:{gridsize} '
    )
    root.insert(0, comment)  # 0 is the index where comment is inserted
    if inkscape:             # add tags so plotter can split on layer
      ET.register_namespace(
        'inkscape',"http://www.inkscape.org/namespaces/inkscape"
      )
      root.set('xmlns:inkscape', "http://www.inkscape.org/namespaces/inkscape")
      self.ns1 = '{http://www.inkscape.org/namespaces/inkscape}'
    #ET.dump(root)
    self.ns = '{http://www.w3.org/2000/svg}'
    self.root = root
    self.inkscape = inkscape

  def make(self):
    ''' expand the doc from gridwalk and convert to XML
    '''
    uniqid = 0 # xml elements must have unique IDs
    for group in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', group['style'])
      if self.inkscape:
        g.set('inkscape:groupmode', "layer") # need namespace for inkscape
        g.set('inkscape:label', self.trimStyle(group['style'])) # e.g "CCC"
      for s in group['shapes']:
        uniqid += 1
        name = s['name']
        #print(name, str(uniqid))
        if name == 'circle':
          circle = ET.SubElement(g, f"{self.ns}circle", id=str(uniqid))
          circle.set('cx', f"{s['cx']:g}")
          circle.set('cy', f"{s['cy']:g}")
          circle.set('r', f"{s['r']:g}")
        #elif name == 'rect':
        elif name == 'square' or name == 'line':
          rect = ET.SubElement(g, f"{self.ns}rect", id=str(uniqid))
          rect.set("x", f"{s['x']:g}")
          rect.set("y", f"{s['y']:g}")
          rect.set("width", f"{s['width']:g}")
          rect.set("height", f"{s['height']:g}")
        #elif name == 'polygon':
        elif name == 'triangl' or name == 'diamond':
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

class LinearSvg(Svg):
  ''' output design to a two dimensional SVG that a plotter can understand
  '''
  def __init__(self, scale, gridsize=None, cellsize=None):
    if gridsize and cellsize:
      super().__init__(unit='mm', scale=scale, gridsize=gridsize, cellsize=cellsize)
    else:
      super().__init__(unit='mm', scale=scale)
    self.labels = list()

  def wireframe(self):
    ''' preview shapes generated by Flatten in order to write meander.conf
        <polygon points="0,100 50,25 50,75 100,0" />
    '''
    inner_p = list()
    b1 = self.blockify()[0]
    #pp.pprint(b1)
    todo = self.makeGeominks(b1)
    f = Flatten()
    f.run(todo)
    s = f.stats
    print(f"""
added {s[0]} merged {s[1]} cropped {s[2]} ignored {s[3]} punched {s[4]}
TOTAL {len(f.done)}""")
    uniqid = 1 # xml elements must have unique IDs
    g      = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g.set('style', 'fill:#FFF;stroke:#000;stroke-width:1')
    for gmk in f.done:
      uniqid += 1
      ''' SVG polygon
      '''
      p      = ET.SubElement(g, f"{self.ns}polygon", id=str(uniqid))
      points = str()
      # print(f"{shape_name=}")
      if gmk.label[0] == 'S':  # Square Ring is a multi part geometry
        outer  = list(gmk.shape.exterior.coords)
        inner  = list(gmk.shape.interiors)
        coords = outer 
        [inner_p.append(list(lring.coords)) for lring in inner]
      else:
        coords = list(gmk.shape.boundary.coords)
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
      p.set("points", points.strip())

    uniqid += 1
    g2 = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g2.set('style', 'fill:#FFF;stroke:#000;stroke-width:1;stroke-dasharray:0.5')
    for coords in inner_p:  
      uniqid += 1
      ''' Add any points from inner ring
      '''
      p      = ET.SubElement(g2, f"{self.ns}polygon", id=str(uniqid))
      points = str()
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
      p.set("points", points.strip())

    for gmk in f.done:
      ''' SVG text is too hard, print to console instead
      '''
      tx = gmk.shape.bounds[0]
      ty = gmk.shape.bounds[1]
      print(f"{gmk.label:>3} {int(tx):>3},{int(ty):>3}")
      ''' stupid SVG text grr...
      t.set("x", str(tx))
      t.set("y", str(ty))
      t.set('font-size', '4')
      t.set('font-family', 'sans-serif')
      t.set('stroke', '#CCC')
      '''

  def make(self, meander_conf=dict()):
    ''' orchestrate the transformation of incoming cells into SVG lines
    '''
    blocks   = self.blockify()
    self.doc = dict()     # reset for regrouping by fill
    for block in blocks:  # layout blocks across the grid
      todo = self.makeGeominks(block)
      f = Flatten()
      f.run(todo)
      self.regroupColors(f.done, meander_conf=meander_conf)
    ''' now that Flatten.done contains two-d cells sort them for SVG layers
        and create SVG elements
    pp.pprint(blocks[:1])
    '''
    self.svgGroup()
    print(f"""
added {f.stats[0]} merged {f.stats[1]} cropped {f.stats[2]} ignored {f.stats[3]} punched {f.stats[4]}
TOTAL {len(f.done)}""")
 
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

  def makeGeominks(self, block):
    ''' convert cells from blockify into Geomink objects
    '''
    geominks = list()

    for cell in block:
      fill = cell['style']  # e.g. FFF
      x, y, w, h = [
        round(float(cell['x'])), 
        round(float(cell['y'])),
        round(float(cell['width'])), 
        round(float(cell['height']))
      ]
      xywh = tuple([x, y, (x + w), (y + h)])
      gmk  = Geomink(xywh=xywh, pencolor=fill)
      geominks.append(gmk)
    return list(reversed(geominks))  # top cells are done first

  def regroupColors(self, done, meander_conf):
    for d in done:
      xy = d.meander.fill(conf=meander_conf)
      if d.pencolor in self.doc:
        self.doc[d.pencolor].append(xy)
      else:
        self.doc[d.pencolor] = list()
        self.doc[d.pencolor].append(xy)

  def svgGroup(self):
    ''' when pencolor is white it will not plot well on white paper
        but it is still allowed here
    '''
    uniqid = 0
    for pencolor in self.doc:
      uniqid += 1
      g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
      g.set('style', f"fill:none;stroke:#{pencolor}")

      for line in self.doc[pencolor]:
        uniqid += 1
        points = str()
        for c in list(line.coords):
          x = c[0]
          y = c[1]
          points += f"{x},{y} "
        polyln = ET.SubElement(g, f"{self.ns}polyline", id=str(uniqid))
        polyln.set("style", 'stroke-width:0.5') # 1mm stripes do not show in gthumb
        polyln.set("points", points)

'''
the
end
'''
