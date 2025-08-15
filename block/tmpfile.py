''' yaml file for conf and csv for palettes
'''
import yaml
import random
import hmac
import pprint
from block import Views, BlockData
from config import *

# TODO add palette

class TmpFile:

  BLOCKSZ = tuple()
  VERSION = 1
  pp      = pprint.PrettyPrinter(indent=2)

  def setVersion(self, ver=None):
    ''' Version is badly named reference to palette index
        0: universal is a mess and should not be used
        using len(fnam) is risky because not enough entries
    '''
    if ver is None:
      ver = random.choice(range(1, len(config.friendly_name)))
    self.VERSION = ver
    return ver

  def write(self, model, cells):
    ''' wrap the data and make ready to write
    '''
    ver   = self.VERSION
    bd    = BlockData(model)
    pos   = bd.readPositions(model)
    fgpos = self.positionBlock(pos)
    topos = self.positionBlock(pos, top=True)
    pal   = config.friendly_name[ver]
    
    celldata = {
      'model': model,
      'palette': config.friendly_name[ver]
    }
    for label in cells:
      cell = cells[label]
      cell = self.refactorCell(label, cell)
      celldata[label] = cell

    posdata = dict()
    posdata['positions'] = { 'foreground': fgpos }
    if topos: posdata['positions']['top'] = topos

    self.writeConf(model, celldata, posdata)

  def writeConf(self, model, celldata, posdata):
    ''' PyYAML flow style None is different from False
        we write twice to get both :/
    '''
    out = yaml.dump(celldata, default_flow_style=False)
    out += yaml.dump(posdata, default_flow_style=None)
    with open(f'conf/{model}.yaml', 'w') as outfile:
      print(out, file=outfile)

  def readConf(self, model, meta=False):
    ''' read YAML
    '''
    meta_tags = ['model', 'palette', 'positions'] # defaults will be popped

    with open(f'conf/{model}.yaml', 'r') as yf:
      conf = yaml.safe_load(yf)

    self.VERSION = conf['palette']
    if meta:
      meta_vals = [conf[key] for key, val in conf.items() if key in meta_tags]
      metadata  = dict(zip(meta_tags, meta_vals))
      return metadata
    else:
      if 'defaults' in conf:      # copy defaults 
        defaults = conf.pop('defaults')
        for key in defaults:
          for val in defaults[key]:
            for cell in conf:
              if key in conf[cell]:
                conf[cell][key][val] = defaults[key][val]

      for tag in meta_tags: del conf[tag] # remove meta data
      for label in conf: # add the hash #rrggbb
        for cs in conf[label]:
          if cs in ['color', 'stroke']:
            for fb in conf[label][cs]:
              if fb in ['fill', 'background']: # skip opacity
                conf[label][cs][fb] = self.prettyHash(conf[label][cs][fb])
    return conf 

  def makeDigest(self, key=None):
    if key is None:
      az  = [chr(i) for i in range(97,123,1)] 
      key = ''.join(random.choice(az) for i in range(12))
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()

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
    rgb = str(val) # rgb must be a string but YAML can send int
    fix = str()
    if remove:          fix = rgb[1:]
    elif rgb[0] == '#': fix = rgb
    else:               fix = '#' + str(rgb)
    return fix 
 
  def refactorCell(self, label, cell):
    print(f'{label} ', end='', flush=True)
    facing = {
        'all': 'C',
      'north': 'N',
       'east': 'E',
      'south': 'S',
       'west': 'W'
    }
    f = cell['facing']
    newc = dict()
    newc['geom'] = {
      'facing': facing[f],
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

'''
the
end
'''

