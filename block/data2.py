import psycopg2
import pprint
from cell.transform import Transform

class BlockData2(Transform):
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  def __init__(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    super().__init__()

  def pens(self, pens, new_ver):
    pen_count = self.pensRead(new_ver)
    #print(f'{new_ver=} {pen_count=}')
    if pen_count:   return 0, pens
    elif pens:      return self.pensWrite(pens, new_ver)
    else:           raise TypeError('expected known ver or new pens')

  def pensRead(self, ver):
    self.cursor.execute("""
SELECT count(*) 
FROM pens
WHERE ver = %s;""", [ver])
    return self.cursor.fetchone()[0]

  def pensWrite(self, pens, new_ver):
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

    for pen in pens:
      _, fill, name = pen  # ignore old ver
      try:
        self.cursor.execute("""
INSERT INTO pens (ver, fill, penam)
VALUES (%s, %s, %s);""", [new_ver, fill, name]
        )
      except psycopg2.errors.UniqueViolation:  # 23505 
        raise KeyError(f'{new_ver=} and {fill=} must be unique')
      new_record_count += 1
    return new_record_count, pens

  def version(self, ver):
    ''' replace non-plottable palettes
        consumers of this class are expected to convert beforehand
    '''
    if ver < 8: # stop right there
      raise ValueError(f'palette conversion needed for {ver}')
    return ver - 7

  def rinks(self, rinkid, mid=0, meta=list(), size=None, factor=None):
    rinkdata = self.rinksRead(rinkid)
    if rinkdata:   
      return 0, rinkdata
    elif mid and len(meta) == 3:
      return self.rinksWrite(rinkid, mid, meta, size, factor)
    else: 
      raise TypeError('cannot create rink without mid and meta')

  def rinksRead(self, rinkid):
    self.cursor.execute("""
SELECT *
FROM rinks
WHERE rinkid = %s;""", [rinkid]
    )
    return self.cursor.fetchone()

  def rinksWrite(self, rinkid, mid, meta, size, factor):
    new_record_count      = 1
    ver, pubdate, created = meta

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
