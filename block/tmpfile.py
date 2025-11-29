''' yaml file for conf and csv for palettes
'''
import yaml
import random
import hmac
import pprint
from block import Views, BlockData, InputValidator
from config import *
from cell import Palette

# TODO add palette

class TmpFile(InputValidator):

  BLOCKSZ   = tuple()
  VERSION   = 1
  pp        = pprint.PrettyPrinter(indent=2)
  meta_tags = ['model', 'palette', 'positions'] # defaults will be popped

  def setVersion(self, ver=None):
    ''' Version is badly named reference to palette index
        0: universal is a mess and should not be used
        using len(fnam) is risky because not enough entries
    '''
    USE_PEN_PALS = 7  # palettes with pens, not friends from abroad :-D
    pal          = Palette()
    fnam         = pal.friendlyPenNames()
    if ver is None:
      ver = random.choice(range(USE_PEN_PALS, len(fnam)))
    self.VERSION = ver
    self.PALETTE = fnam[ver]
    return ver

  def write(self, model, cells):
    ''' wrap the data and make ready to write
    '''
    bd    = BlockData(model)
    pos   = bd.readPositions(model)
    fgpos = self.positionBlock(pos)
    topos = self.positionBlock(pos, top=True)
    
    celldata = dict()
    for label in cells:
      cell = cells[label]
      cell = self.refactorCell(label, cell)
      celldata[label] = cell

    metadata = {
      'model': model,
      'palette': self.PALETTE
    }
    metadata['positions'] = { 'foreground': fgpos }
    if topos: metadata['positions']['top'] = topos

    safecells  = self.validate(celldata)
    if isinstance(safecells, dict):
      self.writeConf(model, metadata, celldata)
    else:
      raise TypeError(safecells)  # error string

  def writeConf(self, model, metadata, celldata):
    ''' PyYAML flow style None is different from False
        we write twice to get both :/
    '''
    out  = yaml.dump(metadata, default_flow_style=None)
    out += yaml.dump(celldata, default_flow_style=False)
    with open(f'conf/{model}.yaml', 'w') as outfile:
      print(out, file=outfile)

  def readConf(self, model, meta=False):
    ''' read YAML
    '''

    with open(f'conf/{model}.yaml', 'r') as yf:
      conf = yaml.safe_load(yf)

    self.VERSION = conf['palette']
    if meta:
      conf = self.readMeta(conf)
    else:
      conf = self.readCells(conf)
    return conf

  def readCells(self, conf):
    if 'defaults' in conf:      # copy defaults 
      defaults = conf.pop('defaults')
      for key in defaults:
        for val in defaults[key]:
          for cell in conf:
            if key in conf[cell]:
              conf[cell][key][val] = defaults[key][val]

    for tag in self.meta_tags: del conf[tag] # remove meta data
    for label in conf: # add the hash #rrggbb
      for cs in conf[label]:
        if cs in ['color', 'stroke']:
          for fb in conf[label][cs]:
            if fb in ['fill', 'background']: # skip opacity
              conf[label][cs][fb] = self.prettyHash(conf[label][cs][fb])
    # handover to pydantic
    safecells  = self.validate(conf)
    if isinstance(safecells, dict):
      self.setDigest(celldata=safecells) 
    else:
      raise TypeError(safecells)  # error string
    return safecells

  def readMeta(self, conf):
    meta_vals = [conf[key] for key, val in conf.items() if key in self.meta_tags]
    metadata  = dict(zip(self.meta_tags, meta_vals))
    return metadata

  def setDigest(self, celldata=None):
    if celldata is None: # non-reversable 
      az  = [chr(i) for i in range(97,123,1)] 
      key = ''.join(random.choice(az) for i in range(12))
    else: key = self.digestString(celldata)
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()

  def digestString(self, celldata):
    ''' create a string that is uniq to rink and repeatable
        hoover all the vals together
    '''
    seed = str()
    for label in celldata: 
      for k in celldata[label]:
        for item in celldata[label][k]:
          seed += str(celldata[label][k][item])
    return seed

  def setBlocksize(self, positions):
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

  def emptyBlock(self):
    block = list(range(self.BLOCKSZ[1]))
    for x in block:
      row      = list(range(self.BLOCKSZ[0]))
      block[x] = row
    return block

  def positionBlock(self, positions, top=False):
    ''' make positions pretty for yaml
    '''
    self.setBlocksize(positions)
    i     = 1 if top else 0
    block = self.emptyBlock()
    for p in positions:
      x, y = p
      block[y][x] = positions[p][i]

    if top: # does this model have any cells with top?
      truth = list()
      for row in block:
        truth.append(all(t is None for t in row))
      if truth.count(True) == len(block): block = None
    return block

  def prettyHash(self, val, remove=False):
    ''' YAML looks nicer with FF00CC but database wants #FF00CC
    '''
    if val is None:  # TODO or FFF ?
      return         # ignore empty background
    rgb = str(val) # rgb must be a string but YAML can send int
    fix = str()
    if remove:          fix = rgb[1:]
    elif rgb[0] == '#': fix = rgb
    else:               fix = '#' + str(rgb)
    return fix 
 
  def refactorCell(self, label, cell):
    print(f'{label} ', end='', flush=True)
    """
    facing = {
        'all': 'C', 'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'
    }
    """
    newc = dict()
    newc['geom'] = {
      'facing': cell['facing'],
        'size': cell['size'],
        'name': cell['shape'],
         'top': cell['top']
    }
    newc['color'] = {
      'fill': self.prettyHash(cell['fill'], remove=True),
   'opacity': cell['fill_opacity'],
'background': self.prettyHash(cell['bg'], remove=True)
    }
    # block.Views.readCelldata treats stroke as optional
    if 'stroke' in cell and cell['stroke'] is not None:
      newc['stroke'] = {
        'fill': cell['stroke'][1:],
        'dasharray': cell['stroke_dasharray'],
        'opacity': cell['stroke_opacity'],
        'width': cell['stroke_width']
      }
    return newc

  def exportPalfile(self, palname, palette):
    ''' write paldata to a tab separated text file

    self.pp.pprint(palette)
    '''
    if len(palette) == 0:
      raise ValueError(f"{palname} is empty")
    with open(f"palettes/{palname}.txt", 'w') as f:
      print("\t".join(['fill', 'opacity', 'background']), file=f)
      for pal in palette:
        line = [str(p) for p in pal] # convert everything to string
        print("\t".join(line), file=f)  # flush=True)

  def importPalfile(self, palname):
    with open(f"palettes/{palname}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    return data

  def getOldColors(self, dig):
    ''' read old colours from palettes/DIGEST.txt

    to generate palettes/DIGEST.txt as list of colour from rink to swap
    ./recurrink clone -d2fcb3c6c178814262c116e16b62c6a19 -opal
    '''
    oc  = set()
    old_pal = self.importPalfile(dig)
    [oc.add(c[0]) for c in old_pal]
    [oc.add(c[2]) for c in old_pal]
    return oc

'''
the
end
'''

