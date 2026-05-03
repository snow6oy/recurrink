import pprint
#from cell import Transform
from cell import Clone as CloneCell
from .palette import PaletteMaker
from .tmpfile import TmpFile
from .data import BlockData

class Clone(BlockData):
  ''' pull from db to create tmp/MODEL.txt from rinkid
  '''
  VERBOSE = False
  pp      = pprint.PrettyPrinter(indent=2)
  #cd      = CellData()
  tf      = TmpFile()
  #tx      = Transform()
  cc      = CloneCell()
  pmk     = PaletteMaker()
  widthmm = 1 # TODO source this from db   

  def palSwap(self, rinkid, ver):
    ''' transform a rink to use a new palette
        e.g sharpie 180f1989f54ff03291ec31e164f2a79f
    '''
    mid, *extra = self.rinks(rinkid)     # lookup model name
    rinkset  = set()                     
    celldata = self.layers(rinkid)    # get colors used by rink
    for label, cell in celldata.items():
      for z, row in enumerate(cell):
        if not len(row): continue
        #print(f'{label} {z} {row[3]}')
        rinkset.add(row[3])
    colors   = self.colors(ver)
    colors   = set([c[0] for c in colors])  # strip out penam
    colors   = self.pmk.setLookUp(colors)   # RGB to search the new colour
    swp, out = self.pmk.swapColors(rinkset, colors)

    yamldata    = dict()

    for label, cell in celldata.items():
      layers = list()
      for z in cell:
        if not len(z): continue
        old_stroke   = z[3]
        new_layer    = list(z)
        new_layer[3] = swp[old_stroke]
        layers.append(tuple(new_layer))
      #self.pp.pprint(layers)
      yamldata[label] = self.cc.databaseToYaml(layers, self.widthmm)
    return mid, yamldata, out

  def palette(self, ver):
    ''' get pen colors
    '''
    return self.colors(ver=ver)

  def rink(self, rinkid):  # we want celldata as YAML
    ''' rink and celldata
    '''
    mid, ver, clen, factor, *dates = self.rinks(rinkid)
    celldata = self.layers(rinkid)
    yamldata = dict()
    for label, cell in celldata.items():
      yamldata[label] = self.cc.databaseToYaml(cell, self.widthmm)
    return mid, ver, yamldata

  def writeConf(self, model, celldata, penam, pos, rinkid):
    self.tf.writePretty(model, celldata, penam, pos, rinkid)
    return f"""
cloning {model}
with {len(celldata)} cells
"""

'''
the
end
'''
