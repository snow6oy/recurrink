import pprint
from model import ModelData
from block import PaletteMaker, TmpFile, BlockData
from cell import CellData
from config import *
#from block.clone import Clone as BlockClone


class Clone:
  ''' pull from db to create tmp/MODEL.txt from rinkid
  '''
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)
  cd      = CellData()
  md      = ModelData()
  bd      = BlockData()
  tf      = TmpFile()
  pmk     = PaletteMaker()

  def palSwap(self, penam, rinkid):
    ''' transform a rink to use a new palette
        e.g sharpie 180f1989f54ff03291ec31e164f2a79f

    print(f'{penam=} {rinkid=}')
    '''
    mid, *extra = self.bd.rinks(rinkid)     # lookup model name
    model = self.md.model(mid=mid)

    rinkset  = set()                        # get colors used by rink
    celldata = self.cd.layers(rinkid)
    for label, cell in celldata.items():
      for z, row in enumerate(cell):
        if not len(row): continue
        #print(f'{label} {z} {row[3]}')
        rinkset.add(row[3])
    pens     = self.md.pens()               # new color set
    ver      = pens.index(penam)
    colors   = self.bd.colors(ver)
    colors   = set([c[0] for c in colors])  # strip out penam
    colors   = self.pmk.setLookUp(colors)   # RGB to search the new colour
    swp, out = self.pmk.swapColors(rinkset, colors)
   
    for label, cell in celldata.items():
      layers = list()
      for z in cell:
        if not len(z): continue
        old_stroke   = z[3]
        new_layer    = list(z)
        new_layer[3] = swp[old_stroke]
        layers.append(tuple(new_layer))
      celldata[label] = layers  # update db colors 
    #self.pp.pprint(celldata)
    out += self.writeConf(model, ver, rinkid, celldata)
    return out + f'palette {penam}'

  def palette(self, rinkid=None, penam=None):
    ''' write pen colors (may not be required if merged with HTML)
    '''
    pens    = self.md.pens()
    palver  = pens.index(penam)
    palette = self.bd.colors(ver=palver)
    tf.dumpUniq('palettes', penam, palette)
    return f"palettes/{penam}.txt was written from db"

  def rink(self, rinkid):  # we want celldata as YAML

    mid, ver, clen, factor, *dates = self.bd.rinks(rinkid)
    model = self.md.model(mid=mid)
    pens  = self.md.pens()
    penam = pens[ver] if 1 <= ver < len(pens) else None
    #print(f'{ver=} {penam=}')
    celldata  = self.cd.layers(rinkid)
    written   = self.writeConf(model, ver, rinkid, celldata)
    return written + f'palette {penam}'

  def writeConf(self, model, ver, rinkid, celldata):
    celldata = self.cd.txDbv3Yaml(celldata)
    self.tf.setVersion(ver)
    self.tf.writePretty(model, celldata, rinkid=rinkid)
    return f"""
cloning {model}
with {len(celldata)} cells
"""

'''
the
end
'''
