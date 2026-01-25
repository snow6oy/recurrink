import psycopg2
import pprint
from cell.transform import Transform

class BlockData2(Transform):
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    super().__init__()

  #def colors(self, colors, ver=0):
  def colors(self, ver, colors=None):
    new_ver   = ver # we can only understand new ver around here OKAY? 
    colors    = self.colorsRead(new_ver)
    pen_count = len(colors)
    #print(f'{new_ver=} {pen_count=}')
    if pen_count:   return 0, colors
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

    for entry in colors:
      _, fill, name = entry  # ignore old ver
      try:
        self.cursor.execute("""
INSERT INTO colors (ver, fill, penam)
VALUES (%s, %s, %s);""", [new_ver, fill, name]
        )
      except psycopg2.errors.UniqueViolation:  # 23505 
        raise KeyError(f'{new_ver=} and {fill=} must be unique')
      new_record_count += 1
    return new_record_count, colors

  def version(self, ver):
    ''' replace non-plottable palettes
        consumers of this class are expected to convert beforehand
    '''
    if ver < 8: # stop right there
      raise ValueError(f'palette conversion needed for {ver}')
    return ver - 7

  def rinks(self, rinkid, mid=0, ver=0, dates=list(), size=None, factor=None):
    rinkdata = self.rinksRead(rinkid)
    if rinkdata:   
      return 0, rinkdata
    elif mid and ver:
      return self.rinksWrite(rinkid, mid, ver, dates, size, factor)
    else: 
      raise TypeError(f'cannot create rink without {mid=} and {ver=}')


  def rinksRead(self, rinkid):
    self.cursor.execute("""
SELECT *
FROM rinks
WHERE rinkid = %s;""", [rinkid]
    )
    return self.cursor.fetchone()

  def rinksWrite(self, rinkid, mid, ver, dates, size, factor):
    new_record_count = 1
    pubdate, created = dates

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
