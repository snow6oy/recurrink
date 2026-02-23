import pprint
import random
from model import ModelData
from block.init  import Init as BlockInit

class Init(ModelData):

  def __init__(self, model=None, pen=None):
    self.mnam  = model
    self.pen   = pen
    super().__init__()

  def setInput(self, mnam=None, pen=None):
    pens   = self.pens()
    models = self.model()

    if not mnam: mnam = random.choice(models[1:])
    if not pen:   pen = random.choice(pens[1:])

    self.mid  = models.index(mnam)
    self.ver  = pens.index(pen)
    
    return mnam, pen

  def generate(self, model, pen):

    # print(f'{self.mid=} {model=} {self.ver=} {pen=}')

    blocks    = self.blocks(self.mid)
    cells     = [cell[0] for pos, cell in blocks.items()]
    top       = [cell[1] for pos, cell in blocks.items() if cell[1]]
    init      = BlockInit(self.ver, cells, top)
    _, csdata = self.compass(self.mid)
    compass   = Compass(csdata)
    src, data = init.generate(compass)
    return src, data

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Compass():
  ''' compass gives direction to models 
  '''
  def __init__(self, compass):
    conf = dict()
    if compass:  # len(compass):
      for r in compass:
        _, cell, pair, facing = r
        if facing not in conf:
          conf[facing] = list()
        if facing == 'C':
          conf[facing].append(cell)
        else:
          conf[facing].append((cell, pair))
      self.conf = conf
    else:
      self.conf = None

  def axis(self):
    return list(self.conf.keys()) if self.conf else list()

  def all(self, cell):
    ''' test if the given cell has been configured and can face all directions
    '''
    if self.conf and 'C' in self.conf and cell in self.conf['C']:
      return True
    else:
      return False

  def one(self, cell):
    ''' define the cell pairs (tuples) that face each other
    '''
    pair, facing = tuple(), str()
    if self.conf:
      for axis in self.axis():
        if axis == 'C':
          continue
        for p in self.conf[axis]:
          if cell in p:
            pair = p
            facing = axis
    return pair, facing

'''
the
end
'''
