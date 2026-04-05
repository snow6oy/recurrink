import pprint
from cell import Init as CellInit
from .data import BlockData
from .tmpfile import TmpFile

class Init(BlockData):
  ''' do BlockData stuff
  '''
  pp = pprint.PrettyPrinter(indent=2)
  tf = TmpFile()

  def generate(self, compass, ver=0, cells=list(), top=list()):
    colors    = self.colors(ver)
    data      = None
    celldata  = dict()
    both      = cells + top
    uniqcells = set(both)
    source    = 'database'
    #print(uniqcells, compass.conf)
    #self.pp.pprint(colors)

    #for cell in ['c']:  # a b c d
    for cell in uniqcells:
      top_yn = True if cell in top else False
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
                top_yn, axis=axis, facing=celldata[other]['geom']['facing']
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

  def writePretty(self, model, data, penam, pos):
    ''' hit the YAML here
    '''
    #self.tf.setVersion(ver)
    self.tf.writePretty(model, data, penam, pos)

'''
the
end
'''
