''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import pprint
from block import Info as BlockInfo
from .data import ModelData
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Info(ModelData):
  ''' list models or display rink metadata

  TODO cleanup print(pmk.cmpPalettes(fnam[args.palver], rinkid))
  '''
  pp = pprint.PrettyPrinter(indent=2)
  bi = BlockInfo()

  def penList(self): 
    pens = self.pens() 
    pens = [f"{i}\t{name}" for i, name in enumerate(pens)]
    return "\n".join(pens)

  def modeList(self):
    ''' models with top and compass count
    ''' 
    return self.stats()

  def position(self, model):
    mid = self.model(name=model)
    pos = self.positionString(mid)
    x = [' '.join(outer) for outer in pos]
    return "\n".join(x)

  def rinkMeta(self, rinkid):
    ''' rink overview
    '''
    mid, ver, size, factor, create, pub = self.bi.rinkMeta(rinkid)
    pens    = self.pens() 
    penam   = pens[ver] if ver else None
    model   = self.model(mid=mid)
    return f"""
-------+----------
 model | {model} ({mid=})
 penam | {penam} ({ver=})
  size | {size}
factor | {factor}
create | {create:%Y-%m-%d}
   pub | {pub}"""

'''
the
end
'''
