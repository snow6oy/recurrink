import pprint
from cell.init import Init as CellInit
from block.data2 import BlockData2

class Init():

  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self, ver, cells=None, top=None):
    self.ver   = ver
    self.cells = cells
    self.top   = top

  def generate(self, compass):
    bd2       = BlockData2()
    _, colors = bd2.colors(self.ver)
    data      = None
    celldata  = dict()
    both      = self.cells + self.top
    uniqcells = set(both)
    source    = 'database'
    #print(uniqcells, compass.conf)
    #self.pp.pprint(colors)

    #for cell in ['c']:  # a b c d
    for cell in uniqcells:
      top_yn = True if cell in self.top else False
      init   = CellInit(colors)
      if compass.conf:
        source = 'compass'
        pair, axis = compass.one(cell)
        #print(f'{pair=} {axis=} {cell=} {top_yn=}')

        if compass.all(cell): 
          data = init.generate(top_yn, facing_c=True)
        elif len(pair):
          for i in range(2):
            other = pair[i] 
            if other in celldata: # already seen
              data = init.generate(
                top_yn, axis=axis, facing=celldata[other]['facing']
              )
            else:
              data = init.generate(top_yn, axis=axis)
        else:
          # print(f"WARNING {cell=} has a broken compass")
          data = init.generate(top_yn, facing_c=True)
      else:
        data = init.generate(top_yn)
      celldata[cell] = data
    return source, celldata

