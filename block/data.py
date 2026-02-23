import psycopg2
import pprint
from cell.transform import Transform

class BlockData(Transform):
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.count = 0
    super().__init__()

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
    rinkdata = self.rinksRead(rinkid)
    if rinkdata and len(rinkvals):
      mid, ver, size, factor, created, pubdate = rinkvals[0]
      #print(f'UPDATE {ver=} {pubdate=}')
      self.rinksUpdate(rinkid, ver, pubdate) # throw away mostly everything
    elif len(rinkvals):
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
    ''' TODO call CellData() remove layers.* dependencies
        remove rinks records
        increment count
    '''
    print('not implemented')

'''
the
end
'''
