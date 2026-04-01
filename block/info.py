''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import pprint
from block import BlockData
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Info(BlockData):
  ''' obtain and clean rink metadata
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def rinkMeta(self, rinkid):
    ''' rinks gives us this
   12, 
palver 0, 
  size [90, 90]
factor Decimal('1.00'), 
create datetime.datetime(2024, 3, 3, 23, 37, 23, 529264), 
   pub datetime.datetime(2024, 3, 5, 0, 0))
    '''
    mid, ver, size, factor, create, pub = self.rinks(rinkid)
    # pre-format to catch cases where rinkdata returns empty vals
    if size: size     = f'{size[0]} x {size[1]}'
    if factor: factor = f'{factor:0.2f}'
    if pub: pub       = f'{pub:%Y-%m-%d}'
    return mid, ver, size, factor, create, pub
'''
the
end
'''
