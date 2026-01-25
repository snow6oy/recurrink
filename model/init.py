import pprint
import random
from model.data2 import ModelData2
from block.init  import Init as BlockInit

class Init():

  def __init__(self, model=None, pen=None):
    self.model = model
    self.pen   = pen

  def generate(self):
    md2       = ModelData2()
    pens      = md2.pens()
    _, models = md2.model()

    if not self.model: self.model = random.choice(models[1:])
    if not self.pen:   self.pen   = random.choice(pens[1:])

    mid = models.index(self.model)
    ver = pens.index(self.pen)
    print(f'{mid=} {self.model=} {ver=} {self.pen=}')

    _, blocks = md2.blocks(mid)
    cells     = [cell[0] for pos, cell in blocks.items()]
    top       = [cell[1] for pos, cell in blocks.items() if cell[1]]
    init      = BlockInit(ver, cells, top)
    _, csdata = md2.compass(mid)
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
