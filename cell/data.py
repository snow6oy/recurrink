import pprint
from .transform import Transform

class CellData(Transform):
  ''' use-cases

CELL    FG  BG  TOP BG
a       y   n   n   n
b       y   y   n   n
c       y   y   y   n
d       n   n   y   y
e       y   n   y   n

TOP has two versions of truth
it is definetly True when a cell position
has both FG and TOP allocated

cells that are marked as TOP but
are uniquely allocated to a position without a FG (e.g. cell d)
are also TOP.
These will be allocated a BG as if they were a FG
but they will NOT be allocated a Top layer

Expected result

cell  z    BGs
--------------------
a     0    n
a     1    y
b     0    y
b     1    y
c     0    y
c     1    y
c     2    y
d     0    y
d     1    y
e     0    n
e     1    y
e     2    y
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.count = 0
    super().__init__()

  def layers(self, rinkid, celldata=dict()):
    ''' each layer has a db record keyed by rinkid, cell and layer
    '''
    data = self.layersRead(rinkid)
    if data and celldata: 
      self.layersUpdate(rinkid, celldata)
    elif celldata:   
      self.layersWrite(rinkid, celldata)
    elif data:
      return data
    else:
      raise ValueError(f'cannot find any layer for {rinkid}')

  def layersRead(self, rinkid):
    ''' read layers by rinkid
    '''
    data = dict()
    self.cursor.execute("""  
SELECT *
FROM layers
WHERE rinkid = %s
ORDER BY cell, layer;""", 
      [rinkid]   # order by cell layer 
    )
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in data: data[label] = list()
      has_content = [True for x in row[3:] if x] # test for empty strings
      if has_content:
        data[label].insert(z, row[3:])
      else:
        data[label].insert(z, tuple())
    return data

  def layersWrite(self, rinkid, celldata=dict()):
    ''' move this to block.data ?
    '''
    self.count = 0 # reset new record counter
    for label, cell in celldata.items():
      self.cellWrite(rinkid, label, cell)

  def cellWrite(self, rinkid, label, cell):
    ''' write cell to layers table
    '''
    for z, row in enumerate(cell): 
      if len(row) < 5 and z ==0:
        row = tuple([None] * 5)
      if len(row) != 5:
        print(f'cannot write {row} because not 5')
        continue
      ''' print(f'{label=} {z} {row}')
      '''
      self.cursor.execute("""
INSERT INTO layers (rinkid, cell, layer, name, size, facing, stroke, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (rinkid, label, z) + row
      )
      self.count += 1

  def layersUpdate(self, rinkid, celldata):
    ''' layers are immutable except for color swaps
    '''
    self.count = 0
    for label, cell in celldata.items():
      for z, row in enumerate(cell):
        if len(row):
          self.cursor.execute("""
UPDATE layers
SET stroke   = %s
WHERE rinkid = %s
AND cell     = %s
AND layer    = %s;""", (row[3], rinkid, label, z)
          )
          self.count += 1
    #print(f'{self.count=}')
'''
the
end
'''
