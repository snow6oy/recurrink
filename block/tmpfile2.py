import pprint
from model.data2 import ModelData2
from block.data2 import BlockData2
from cell.data2 import CellData2
from cell.transform import Transform

# TODO merge with TmpFile

class TmpFile2(Transform):

  BLOCKSZ = tuple()
  VERBOSE = True

  def __init__(self):
    self.pp     = pprint.PrettyPrinter(indent=2)

  def rinkMeta(self, rinkdata):
    ''' gather metadata from db to write conf/MODEL.yaml
    '''
    md2      = ModelData2()
    _, model = md2.model(mid=rinkdata[1])
    if self.VERBOSE: print(f'got {model=}')
    _, pos   = md2.blocks(mid=rinkdata[1])
    if self.VERBOSE: print(f'got {len(pos)=} blocks')
    pens     = md2.pens(ver=rinkdata[2])
    if self.VERBOSE: print(f'got {pens=}')

    metadata = {
      'id': rinkdata[0],
      'model': model,
      'palette': pens
    }
    fgpos = self.positionBlock(pos)
    topos = self.positionBlock(pos, top=True)
    metadata['positions'] = { 'foreground': fgpos }
    if topos: metadata['positions']['top'] = topos
 
    return model, metadata

  # move to tmpfile # move to tmpfile # move to tmpfile # move to tmpfile 
  def cellData(self, rinkdata):
    ''' gather celldata from db to write conf/MODEL.yaml
    '''
    cd2     = CellData2()
    bd2     = BlockData2()
    rinkid  = rinkdata[0]
    _, geom = cd2.geometry(rinkid)
    if self.VERBOSE: print(f'got {len(geom)=}')
    _, stk  = cd2.strokes(rinkid, rinkdata[2])
    if self.VERBOSE: print(f'got {len(stk)=}')
    _, pal  = cd2.palette(rinkid, rinkdata[2])
    if self.VERBOSE: print(f'got {len(pal)=}')

    celldata      = dict()
    ######################
    for label in geom:
      #print(f'{label=} {len(geom[label])}')
      g = dict(zip(['name', 'size', 'facing'], geom[label][-1]))
      z = len(geom[label]) 
      g['top'] = True if z == 3 else False
      p  = dict(zip(['fill', 'opacity'], pal[label][-1]))
      p['background'] = pal[label][0][0] if z > 1 else None

      if label in stk and stk[label][1][0]: 
        s = dict(zip(['fill', 'opacity', 'width', 'dasharray'], stk[label][1]))
        celldata[label] = {
          'geom': g,
        'stroke': s,
         'color': p
        }
      else: 
        celldata[label] = { 'geom': g, 'color': p }
    _, rinkdata = bd2.rinks(rinkid)
    if self.VERBOSE: print(f'got {len(rinkdata)=}')
    '''
    self.pp.pprint(pal)
    self.pp.pprint(pos)
    self.pp.pprint(rinkdata)
    self.pp.pprint(celldata)
    '''
    return celldata

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
'''
the
end
'''
