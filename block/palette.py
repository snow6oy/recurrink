import math
import pprint
import random
from colorsys import rgb_to_hsv, hsv_to_rgb
from .tmpfile import TmpFile

pp = pprint.PrettyPrinter(indent = 2)

class PaletteMaker:
  ''' palette logic
  '''
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

  def colour_check(self, p, palette):
    ''' compare the new palette against the main colour list
        return a list of those that are missing
    '''
    colours = p.read_colours()
    fill = set([p[0] for p in palette])
    backgrounds = set([p[2] for p in palette])
    for c in colours:
      if c in fill:
        fill.remove(c)
      if c in backgrounds:
        backgrounds.remove(c)
    missing = list(fill) + list(backgrounds)
    return set(missing)

  def collapse_opacity(self, ver, pal):
    ''' for each opacity to be collapsed
        select palette entry with bad opacity
        find nearest pid
        update cells table so view with old pid uses new pid
    '''
    pal.load_palette(ver=ver)
    #new_pid = pal.read_pid(['#C71585', '#FFF', '0.9'])
    for old_fo in [0.6]:  # 9, 0.7, 0.4, 0.3, 0.1]:
      #print(old_fo)
      to_clean = [p for p in pal.palette if p[1] == old_fo]
      for tc in to_clean:
        old_pid = pal.read_pid([tc[0], tc[2], tc[1]])
        new_opacity, new_pid = self.find_opacity(ver, tc, pal)
        if new_pid:
          print(f"UPDATE cells SET pid = {new_pid} WHERE pid = {old_pid};")
        else:
          pass
          #relation = self.relation(tc[0], tc[2])
          #print(f"INSERT INTO palette (ver, fill, bg, opacity, relation) VALUES (0,'{tc[0]}', '{tc[2]}', {new_opacity}, {relation});")

  def find_opacity(self, ver, tc, pal):
    ''' find the nearest opacity to the one we want to deprecate
        return the nearest op and pid, if it already exists in db
    '''
    old_fo = tc[1]
    available = pal.read_cleanpids([tc[0], tc[2]])
    #pp.pprint(available)
    candidates = list()
    for candidate in [1, 0.8, 0.5, 0.2]:
      if candidate > old_fo:
        nearest = (candidate * 10) - (old_fo * 10)
      else:
        nearest = (old_fo * 10) - (candidate * 10)
      pid = None
      for a in available:
        if candidate == a[1]: # compare opacities
          pid = a[0]
          break
      candidates.append([candidate, int(nearest), pid])
    new_pid = sorted(candidates, key=lambda x: x[1], reverse=False)
    #pp.pprint(new_pid)
    return new_pid[0][0], new_pid[0][2]

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

  def makeUnique(self, ver, pal, txtpal):
    ''' compare db and txt palettes and return difference
    '''
    new_pal = list()
    for p in txtpal: # avoid duplicating existing entry
      p[1] = float(p[1])
      test_entry = tuple(p[:3]) 
      if (test_entry not in pal.palette): # its empty the very first time
        new_pal.append(list(test_entry))
    for n in new_pal: # decorate palette before INSERTing
      rn = self.relation(n[0], n[2])
      n.append(rn)
      n.insert(0, ver)
    pal.create_palette_entry(new_pal)
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
    pal  = self.readInkscapePal(paldir, fn)
    print(paldir, fn)
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
    '''
    data = getHex('/home/gavin/.config/inkscape/palettes/', 'uniball.gpl')
    '''
    found = list()
    with open(f"{paldir}/{fn}") as pal:
      for line in pal.read().splitlines():
        bits   = line.split()
        if bits[0] == 'GIMP' or bits[0] == 'Name:':
          continue
        r, g, b, *comments   = bits
        R, G, B = [int(r), int(g), int(b)]
        hexstr  = f'#{R:02x}{G:02x}{B:02x}'
        #print(r, g, b, hexstr)
        found.append(hexstr)
    return tuple(found)
'''
the
end
'''
