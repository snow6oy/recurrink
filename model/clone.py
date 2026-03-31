import pprint
from model import ModelData, SvgPalette
from block.clone import Clone as BlockClone
#from block import PaletteMaker, TmpFile, BlockData
#from cell import CellData
#from config import *

class Clone(ModelData):
  ''' pull from db to create tmp/MODEL.txt from rinkid
  '''
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)
  bc      = BlockClone()
  svgpal  = SvgPalette()

  def palSwap(self, penam, rinkid):
    ''' wrapper to block.clone
    '''
    pens     = self.pens()               # new color set
    ver      = pens.index(penam)

    mid, celldata, out = self.bc.palSwap(rinkid, ver)
    model = self.model(mid=mid)
    out  += self.bc.writeConf(model, ver, rinkid, celldata)
    return out + f'palette {penam}'

  def palette(self, penam):
    ''' write pen colors to HTML
    '''
    pens    = self.pens()
    palver  = pens.index(penam)
    palette = self.bc.palette(ver=palver)
    self.svgpal.render(penam, palette)
    return f"palettes/{penam}.html was written"

  def rink(self, rinkid):  # we want celldata as YAML

    mid, ver, celldata = self.bc.rink(rinkid)
    model              = self.model(mid=mid)
    pens               = self.pens()
    penam   = pens[ver] if 1 <= ver < len(pens) else None
    written = self.bc.writeConf(model, ver, rinkid, celldata)
    return written + f'palette {penam}'
'''
the
end
'''
