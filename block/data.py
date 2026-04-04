import psycopg2
import pprint
from config import Db2
#from cell.transform import Transform

class BlockData(Db2):
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  pp    = pprint.PrettyPrinter(indent=2)
  count = 0

  def colors(self, ver, colors=None):
    ''' pen sets were re-defined in the pens table
new_ver old_ver
1       8       uniball
2       11      copicsketch
3       9       copic
4       10      stabilo68
5       12      sharpie
6       13      staedtler
    '''
    new_ver   = ver # we can only understand new ver around here OKAY? 
    found     = self.colorsRead(new_ver)
    pen_count = len(found)
    #print(f'{new_ver=} {pen_count=} {len(colors)=}')
    if pen_count:   return found
    elif colors:    return self.colorsWrite(colors, new_ver)
    else:           raise TypeError(f'expected known ver {ver=} or new colors')

  def colorsRead(self, ver):
    self.cursor.execute("""
SELECT fill, penam
FROM colors
WHERE ver = %s;""", [ver])
    #return self.cursor.fetchone()[0]
    return self.cursor.fetchall()

  def colorsWrite(self, colors, new_ver):
    ''' copy from gplfile to db

          fill       penam
        { '#000000': '46', '#0000aa': '32' }
    '''
    self.count = 0
    for fill, name in colors.items(): 
      try:
        self.cursor.execute("""
INSERT INTO colors (ver, fill, penam)
VALUES (%s, %s, %s);""", [new_ver, fill, name]
        )
      except psycopg2.errors.UniqueViolation:  # 23505 
        raise KeyError(f'{new_ver=} and {fill=} must be unique')
      self.count += 1

  def version(self, ver):
    ''' replace non-plottable palettes
        consumers of this class are expected to convert beforehand
    '''
    if ver < 8: # palette conversion will be needed later
      return 0
    return ver - 7

  def rinks(self, rinkid, *rinkvals):
    ''' when rinkid exists in database and rinkvals == 4
        there will be not enough vals to unpack error
        del rinkid and try again
    '''
    rinkdata = self.rinksRead(rinkid)
    if len(rinkvals): incoming = rinkvals[0]
    else:             incoming = None 
    if rinkdata and incoming:
      mid, ver, size, factor, created, pubdate = rinkvals[0]
      #print(f'UPDATE {ver=} {pubdate=}')
      self.rinksUpdate(rinkid, ver, pubdate) # throw away mostly everything
    elif incoming:
      mid, ver, size, factor = rinkvals[0]
      #print(f'INSERT {mid=} {ver=} {size=} {factor=}')
      self.rinksWrite(rinkid, mid, ver, size, factor)
    elif rinkdata:
      return rinkdata
    # NOT FOUND 

  def rinksRead(self, rinkid):
    self.cursor.execute("""
SELECT mid, ver, clen, factor, created, pubdate
FROM rinks
WHERE rinkid = %s;""", [rinkid]
    )
    return self.cursor.fetchone()

  '''
  def rinksWrite(self, rinkid, mid, ver, clen, factor, created, pubdate):
    rinkdata = tuple(
      [rinkid, mid, ver, size, factor, created, pubdate]
    )
  '''
  def rinksWrite(self, rinkid, mid, ver, size, factor):
    self.count = 0
    clen       = f'{{{size}, {size}}}'
    self.cursor.execute("""
INSERT INTO rinks (rinkid, mid, ver, clen, factor, created, pubdate)
VALUES (%s, %s, %s, %s, %s, DEFAULT, DEFAULT);""",
      (rinkid, mid, ver, clen, factor)
    )
    self.count = 1

  def rinksUpdate(self, rinkid, ver, pubdate):
    ''' rinks are immutable with the exception of ver and pubdate
    '''
    self.count = 0
    self.cursor.execute("""
UPDATE rinks
SET ver = %s, pubdate = %s
WHERE rinkid = %s;""", (ver, pubdate, rinkid)
    )
    self.count = 1

  def rinksDelete(self, rinkid):
    ''' remove layers.* dependencies
        and then remove rinks records
        increment and return count
    '''
    self.count = 0
    self.cursor.execute("""
DELETE from layers 
WHERE rinkid = %s
RETURNING *;""", [rinkid]
    )
    self.count = len(self.cursor.fetchall())

    self.cursor.execute("""
DELETE from rinks
WHERE rinkid = %s
RETURNING *;""", [rinkid]
    )
    self.count += len(self.cursor.fetchall())
    return f'num of records deleted: {self.count}'

  def layers(self, rinkid, celldata=dict()):
    ''' each layer has a db record keyed by rinkid, cell and layer
        use-cases

CELL    FG  BG  TOP BG
a       y   n   n   n
b       y   y   n   n
c       y   y   y   n
d       n   n   y   y
e       y   n   y   n

TOP has two versions of truth it is definetly True when a cell position
has both FG and TOP allocated. Cells that are marked as TOP but
are uniquely allocated to a position without a FG (e.g. cell d)
are also TOP. These will be allocated a BG as if they were a FG
but they will NOT be allocated a Top layer. BGs can be empty

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
