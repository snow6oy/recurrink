''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import pprint
from model import ModelData
from block import BlockData
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Info:
  ''' list models or display rink metadata

  TODO cleanup print(pmk.cmpPalettes(fnam[args.palver], rinkid))
  '''
  pp = pprint.PrettyPrinter(indent=2)
  md = ModelData()
  bd = BlockData()

  def listPens(self): 
    pens = self.md.pens() 
    pens = [f"{i}\t{name}" for i, name in enumerate(pens)]
    return "\n".join(pens)

  def position(self, model):
    mid = self.md.model(name=model)
    pos = self.md.positionString(mid)
    x = [' '.join(outer) for outer in pos]
    return "\n".join(x)

  def rinkMeta(self, rinkid):
    pens = self.md.pens() 
    ''' rinks gives us this
   12, 
palver 0, 
  size [90, 90]
factor Decimal('1.00'), 
create datetime.datetime(2024, 3, 3, 23, 37, 23, 529264), 
   pub datetime.datetime(2024, 3, 5, 0, 0))
    '''
    mid, ver, size, factor, create, pub = self.bd.rinks(rinkid)
    # pre-format to catch cases where rinkdata returns empty vals
    if size: size     = f'{size[0]} x {size[1]}'
    if factor: factor = f'{factor:0.2f}'
    if pub: pub       = f'{pub:%Y-%m-%d}'
    penam             = pens[ver] if ver else None
    model             = self.md.model(mid=mid)
    return f"""
-------+----------
 model | {model} ({mid=})
 penam | {penam} ({ver=})
  size | {size}
factor | {factor}
create | {create:%Y-%m-%d}
   pub | {pub}"""

  def stats(self):
    ''' working on it
    ''' 
    return self.md.stats()

'''
the
end
'''
