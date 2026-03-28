''' yaml file for conf and csv for palettes
'''
import yaml
import random
import hmac
import pprint
from model import ModelData
from block import BlockData, InputValidator
from cell import CellData
# from config import *
# db2 will change once data2 merges
# from cell.data import CellData

class TmpFile(InputValidator):

  BLOCKSZ   = tuple()
  VERSION   = 1
  VERBOSE   = False
  pp        = pprint.PrettyPrinter(indent=2)
  meta_tags = ['id', 'model', 'palette', 'positions'] # defaults will be popped

  def setVersion(self, ver=None):
    ''' Version is badly named reference to palette index
        0: universal is a mess and should not be used
        using len(fnam) is risky because not enough entries
    '''
    USE_PEN_PALS = 7  # palettes with pens, not friends from abroad :-D
    md           = ModelData()
    fnam         = md.pens()
    '''
    pal          = Palette()
    fnam         = pal.friendlyPenNames()
    md2  = ModelData2()
    fnam = md2.pens()
    ver  = int(ver)
    '''

    if ver is None: ver = random.choice(range(USE_PEN_PALS, len(fnam)))
    self.VERSION = ver
    self.PALETTE = fnam[ver]
    return ver

  def writePretty(self, model, celldata, rinkid=None):
    ''' make the fills pretty be removing # 
    '''
    for label in celldata: # remove the hash in #rrggbb
      print(f'{label} ', end='', flush=True)
      for cs in celldata[label]:
        if cs in ['color', 'stroke']:
          for fb in celldata[label][cs]:
            if fb in ['fill', 'background']: # skip opacity
              celldata[label][cs][fb] = self.prettyHash(
                celldata[label][cs][fb], remove=True
              )
              #print(f'{label=} {cs=} {fb=}')
    print()
    metadata = self.metadata(model, rinkid)
    self.writeConf(model, metadata, celldata)
    
  def writeConf(self, model, metadata, celldata):
    ''' PyYAML flow style None is different from False
        we write twice to get both :/
    '''
    out  = yaml.dump(metadata, default_flow_style=None)
    out += yaml.dump(celldata, default_flow_style=False)
    with open(f'conf/{model}.yaml', 'w') as outfile:
      print(out, file=outfile)

  def metadata(self, model, rinkid=None):
    ''' compile metadata for conf
    '''
    md       = ModelData()
    mid      = md.model(name=model)
    pos      = md.positionString(mid)
    metadata = {
      'id': rinkid,
      'model': model,
      'palette': self.PALETTE,
      'positions': pos
    }
    return metadata

  def readConf(self, model, meta=False):
    ''' read YAML
    '''

    with open(f'conf/{model}.yaml', 'r') as yf:
      conf = yaml.safe_load(yf)

    self.VERSION = conf['palette']
    if meta: conf = self.readMeta(conf)
    else:    conf = self.readCells(conf)
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
    meta_val = [conf[key] for key, val in conf.items() if key in self.meta_tags]
    metadata = dict(zip(self.meta_tags, meta_val))
    return metadata

  def setDigest(self, celldata=None):
    if celldata is None: # non-reversable 
      az  = [chr(i) for i in range(97,123,1)] 
      key = ''.join(random.choice(az) for i in range(12))
    else: key = self.digestString(celldata)
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()
    return self.digest

  def digestString(self, celldata):
    ''' create a string that is uniq to rink and repeatable
        hoover all the vals together
    '''
    seed = str()
    for label in celldata: 
      for k in celldata[label]:
        if celldata[label][k] is None: # empty strokes became None
          continue
        for item in celldata[label][k]:
          seed += str(celldata[label][k][item])
    return seed

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
 
  ''' write paldata to a tab separated text file
  
  as palettes are no longer editable these functions are
  to be deprecated once consumers migrate
  '''
  def exportPalfile(self, palname, palette):

    self.pp.pprint(palette)
    if len(palette) == 0:
      raise ValueError(f"{palname} is empty")
    with open(f"palettes/{palname}.txt", 'w') as f:
      print("\t".join(['fill', 'penam']), file=f)
      for fill, penam in palette.items():
        print(f'{str(fill)}\t{str(penam)}', file=f)  # flush=True)

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

  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def rinkMeta(self, rinkdata):
    ''' gather metadata from db to write conf/MODEL.yaml
    '''
    md    = ModelData()
    rinkid, mid, ver = rinkdata[:3]
    if self.VERBOSE: print(f'{rinkid=} {mid=} {ver=}')

    model = md.model(mid=rinkdata[1])
    if self.VERBOSE: print(f'{model=}')
    #pos   = md.blocks(mid=rinkdata[1])
    #if self.VERBOSE: print(f'got {len(pos)=} blocks')
    pens     = md.pens(ver=rinkdata[2])
    if self.VERBOSE: print(f'{pens=}')

    metadata = {
      'id': rinkdata[0],
      'model': model,
      'palette': pens
    }
    pos = md.positionString(mid) # convert to nested array
    #topos = self.positionBlock(pos, top=True)
    metadata['positions'] = pos
    #if topos: metadata['positions']['top'] = topos
 
    return model, metadata
'''
the
end
'''
