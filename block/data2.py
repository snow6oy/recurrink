import psycopg2
import pprint
from config import Db2
from cell.transform import Transform

class BlockData2(Transform):
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  def __init__(self):
    self.pp     = pprint.PrettyPrinter(indent=2)

  def pens(self, pens, ver):
    new_ver   = self.version(ver)
    pen_count = self.pensRead(new_ver)
    #print(f'{ver=} {new_ver=} {pen_count=}')
    if pen_count:   return 0, pens
    elif pens:      return self.pensWrite(pens, new_ver)
    else            raise TypeError('expected known ver or new pens')

  def pensRead(self, ver):
    self.cursor.execute("""
SELECT count(*) 
FROM pens
WHERE ver = %s;""", [ver])
    return self.cursor.fetchone()[0]

  def pensWrite(self, pens, ver):
    ''' pen sets are defined in the inkpal table
        currently there are six
new_ver old_ver
1       8       uniball
2       11      copicsketch
3       9       copic
4       10      stabilo68
5       12      sharpie
6       13      staedtler
    '''
    new_record_count = 0
    new_pen          = tuple()

    for pen in pens:
      tmp     = list(pen)
      tmp[0]  = new_ver
      new_pen = tuple(tmp)
      if pcount == 0:
        #print(new_pen)
        try:
          self.cursor.execute("""
INSERT INTO pens (ver, fill, penam)
VALUES (%s, %s, %s);""", new_pen
          )
        except psycopg2.errors.UniqueViolation:  # 23505 
          raise KeyError(f'{ver=} and {fill=} must be unique')
        new_record_count += 1
    return new_record_count, new_pen

  def version(self, ver):
    ''' attempt to replace non-plottable palettes
    '''
    if ver < 8: # stop right there
      raise ValueError(f'palette conversion needed for {ver}')
    return ver - 7

  def rinks(self, rinkid, mid=0, meta=list(), size=None, factor=None):
    rinkdata = self.rinksRead(rinkid)
    if rinkdata:   
      return 0, rinkdata
    elif mid and len(meta) == 3:
      return self.rinksWrite(mid, meta, size, factor)
    else: 
      raise TypeError('cannot create rink without mid and meta')

  def rinksRead(self, rinkid):
    self.cursor.execute("""
SELECT *
FROM rinks
WHERE rinkid = %s;""", [rinkid]
    )
    return self.cursor.fetchone()

  def rinksWrite(self, mid, meta, size, factor):
    new_record_count      = 1
    ver, pubdate, created = meta
    ver                   = self.version(ver)

    self.cursor.execute("""
INSERT INTO rinks (rinkid, mid, ver, clen, factor, created, pubdate)
VALUES (%s, %s, %s, %s, %s, %s, %s);""",  
        (rinkid, mid, ver, size, factor, created, pubdate)
    )
    rinkdata = tuple(
      [rinkid, mid, ver, size, factor, created, pubdate]
    )
    return new_record_count, rinkdata

'''
the
end
'''
