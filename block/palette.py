import math
import pprint
import random
from math import sqrt
from colorsys import rgb_to_hsv, hsv_to_rgb
from .tmpfile import TmpFile

class PaletteMaker:
  ''' palette logic
  '''
  VERBOSE = False
  BADLEN  = {
    '#FFF': '#ffffff',
    '#CCC': '#cccccc',
    '#000': '#000000',
    '#F00': '#ff0000',
    '#FF0': '#ffff00',
    '#00F': '#0000ff',
    '#F0F': '#ff00ff',  
    '#0FF': '#000fff'
  }
  pp      = pprint.PrettyPrinter(indent = 2)

  def rgb_int(self, r, g, b):
    ''' the compliment of #dc143c is #14dcb4
      https://www.w3schools.com/colors/colors_hexadecimal.asp
      https://www.educative.io/answers/how-to-convert-hex-to-rgb-and-rgb-to-hex-in-python
      https://stackoverflow.com/questions/40233986/python-is-there-a-function-or-formula-to-find-the-complementary-colour-of-a-rgb
      returns RGB components of complementary color as int
    '''
    hsv = rgb_to_hsv(r, g, b)
    rgb_float = hsv_to_rgb((hsv[0] + 0.5) % 1, hsv[1], hsv[2])
    return [int(f) for f in rgb_float]

  def hex_rgb(self, hexstr):
    ''' slice into a list e.g. ['dc', '14', '3c']
    '''
    hexitems = [hexstr[1:3], hexstr[3:5], hexstr[5:]]
    # convert to base 16
    return [int(h,16) for h in hexitems]

  def relation(self, fill, bg):
    if len(fill) ==4:
      fill = f"#{fill[1]*2}{fill[2]*2}{fill[3]*2}".lower()
    if len(bg) ==4:
      bg = f"#{bg[1]*2}{bg[2]*2}{bg[3]*2}".lower()
    s = self.secondary(fill)
    #print(f"fill {fill} bg {bg} secondary {s}")
    if bg == fill:
      return 1
    elif bg == s:
      return 2
    else:
      return 0

  def secondary(self, fill=None):
    if fill:
      r, g, b = self.hex_rgb(fill)
      R, G, B = self.rgb_int(r, g, b)
      #return (fill, f'#{R:02x}{G:02x}{B:02x}')
      return f'#{R:02x}{G:02x}{B:02x}'
    else:
      raise ValueError('fill is required')

  def cmpPalettes(self, digest, fn):
    ''' count matching entries of two palettes
    '''
    tf = TmpFile()
    p1 = tf.importPalfile(digest)
    p2 = tf.importPalfile(fn)
    #pp.pprint(p1)
    #pp.pprint(p2)
    same = 0
    for x in p1:
      for y in p2:
        if x[0] == y[0] and x[1] == y[1] and x[2] == y[2]:
          # print(x)
          same += 1
    out = (f"""
{len(new_pal):3d} {digest}
{len(candidate):3d} {fn}
{same:3d} matching palette entries""")
    return out

  def makeUnique(self, ver, dbpal, txtpal):
    ''' compare db and txt palettes and return difference
    '''
    new_pal     = list()

    for p in txtpal: # avoid duplicating existing entry
      p[1]       = float(p[1])
      test_entry = tuple(p[:3]) 
      if (test_entry not in dbpal): # its empty the very first time
        new_pal.append(list(test_entry))
    for n in new_pal: # decorate palette with ver relations before returning
      rn = self.relation(n[0], n[2])
      n.append(rn)
      n.insert(0, ver)
    return new_pal

  ''' INKSCAPE
  '''
  def randomTwo(self, data):
    '''
    '''
    colours   = [random.choice(data) for i in range(2)]
    duocolour = set(colours)
    return duocolour
  
  def inkscapePal(self, paldir, fn):
    ''' convert a list into a set of unique pairs for overprinting fun
    '''
    penpal  = self.readInkscapePal(paldir, fn)
    pal  = list(penpal.keys())
    n    = len(pal)
    size = math.comb(n, 2)
    done = set()
    while len(done) < size:
      rnd2 = self.randomTwo(pal)
      while len(rnd2) != 2:
        # print('.', end='', flush=True)
        rnd2 = self.randomTwo(pal)
      c1, c2 = rnd2
      done.add(f'{c1} 0.5 {c2}')
    '''
    print(len(done))
    '''
    as_list = [d.split() for d in done]
    return as_list

  def readInkscapePal(self, paldir, fn):
    ''' paldir is set in config.py
        fn: 'uniball.gpl'
    '''
    found = dict()
    with open(f"{paldir}/{fn}") as pal:
      for line in pal.read().splitlines():
        bits   = line.split()
        if bits[0] == 'GIMP' or bits[0] == 'Name:' or bits[0] == '#':
          continue
        r, g, b, *comments   = bits
        R, G, B = [int(r), int(g), int(b)]
        hexstr  = f'#{R:02x}{G:02x}{B:02x}'
        penam   = ' '.join(comments[1:])
        #print(r, g, b, hexstr, penam)
        found[hexstr] = penam
    return found

  def updateCells(self, celldata, swp):
    ''' apply new color set to celldata
    '''
    for label in celldata:
      for k in ['bg', 'fill', 'stroke']:
        if k in celldata[label]:
          oc = celldata[label][k]
          if k == 'bg' and oc in ['#FFF', '#fff', '#ffffff']:
            #print('make null background')
            celldata[label][k] = None
          #elif k == 'stroke' and oc not in swp:
          elif oc in swp:
            celldata[label][k] = swp[oc]
          else:
            raise KeyError(f'{label=} {k=} {oc=} not found')
    return celldata

  def setLookUp(self, uniqfill):
    ''' prepare table of new colours for lookup
    '''
    colours = list()
    for uf in uniqfill:
      if uf in self.BADLEN:
        rgb = self.hex_rgb(self.BADLEN[uf])
      elif uf and len(uf) == 7:
        rgb = self.hex_rgb(uf)
      if uf: colours.append(tuple(rgb))
    return colours

  def swapColors(self, oc, nc):
    ''' find the new colour that is closest to the old
        and replace
    '''
    print('-' * 15)
    swp = dict()
    for old_color in oc:
      if old_color == 'None': continue # strokes do not have backgrounds
      anylen = old_color
      if old_color in self.BADLEN:
        anylen = self.BADLEN[old_color]
      elif old_color and len(old_color) < 7:
        raise ValueError(f'{old_color} has bad length')
      rgb       = self.hex_rgb(anylen)
      new_color = self.closestColor(rgb, nc)
      nc_hex    = self.rgbToHex(new_color)
      print(old_color, nc_hex)
      swp[old_color] = nc_hex
    print()
    return swp

  def closestColor(self, rgb, nc):
    ''' do The Real Work right here!
    '''
    r, g, b = rgb
    color_diffs = []
    for color in nc:
      cr, cg, cb = color
      color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
      color_diffs.append((color_diff, color))
    return min(color_diffs)[1]

  def rgbToHex(self, rgb):
    r, g, b = rgb
    ## Ensure values are within 0-255 range
    r = max(0, min(r, 255))
    g = max(0, min(g, 255))
    b = max(0, min(b, 255))

    ## Convert to hexadecimal and remove '0x' prefix
    hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    return hex_color
'''
the
end
'''
