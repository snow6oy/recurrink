import pprint
import psycopg2
from cell.transform import Transform

class ModelData2(Transform):
  ''' access to models, blocks, compass and pens table
  '''
  def __init__(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    super().__init__()

  def model(self, name=None, mid=0):
    ''' retrieve or create and retrieve a model id from a name
        OR given a model ID, retrieve a name
        given neither, return a list of models
    '''
    new_record_count = 0
    models           = self.modelRead()
    if name in models: found = models.index(name) # ID or 0 if name is None
    else:              found = False

    if found:  return new_record_count, found
    elif name: return self.modelWrite(name) 
    elif mid:  return new_record_count, models[mid]
    else:      return new_record_count, models

  def modelRead(self):
    self.cursor.execute("""
SELECT *
FROM models;""")
    models = [row[1] for row in self.cursor.fetchall()]
    models.insert(0, None)  # avoid zero-based model list
    return models

  def modelWrite(self, name):
    ''' create and return model ID
    '''
    self.cursor.execute("""
INSERT INTO models (mid, model)
VALUES (DEFAULT, %s)
RETURNING mid;""", [name])
    mid = self.cursor.fetchone()
    new_record_count = 1
    return new_record_count, mid[0]

  def blocks(self, mid, blocks_v1=dict()):
    ''' attempt to retrieve with mid else add new rows from db v1 values
    
        pos = {(11, 11): ('x', None)}
    '''
    blocks = self.blocksRead(mid)
    if len(blocks):      return 0, blocks
    elif len(blocks_v1): return self.blocksWrite(mid, blocks_v1)
    else:                raise TypeError(f'missing either {mid} or {blocks_v1}')

  def blocksRead(self, mid):
    ''' read blocks by mid and return a dict
    '''
    blocks = dict()
    self.cursor.execute("""
SELECT *
FROM blocks
WHERE mid = %s;""", [mid])
    for row in self.cursor.fetchall():
      key = tuple(row[1])
      blocks[key] = tuple(row[2:])
    return blocks


  def blocksWrite(self, mid, blocks):
    ''' write block from same format as blocksRead returns
    '''
    new_record_count = 0

    for position, celltop in blocks.items():
      p0, p1    = position
      pos_int   = f'{{ {p0}, {p1} }}'  # format postgres style
      cell, top = celltop
      self.cursor.execute("""
INSERT INTO blocks (mid, position, cell, top)
VALUES (%s, %s, %s, %s);""", (mid, pos_int, cell, top)
      )
      new_record_count += 1
    return new_record_count, blocks

  def compass(self, mid, conf=None):
    ''' retrieve compass entries by mid, optionally add new
    '''
    entries = self.compassRead(mid)
    if len(entries):          return 0, entries
    elif conf and len(conf):  return self.compassWrite(mid, conf)
    else:                     return 0, None

  def compassWrite(self, mid, conf):
    new_record_count = 0
    entries = list()
    for k, item in conf.items():
      if k == 'C':    # pair is undefined
        entry = list([mid, item[0], None, k]) 
      else:
        entry = list([mid, item[0][0], item[0][1], k]) # cell and pair

      self.cursor.execute("""
INSERT INTO compass (mid, cell, pair, facing)
VALUES (%s, %s, %s, %s);""", entry
      )
      entries.append(entry)
      new_record_count += 1
    return new_record_count, entries

  def compassRead(self, mid):
    self.cursor.execute("""
SELECT *
FROM compass
WHERE mid = %s;""", [mid])
    entries = self.cursor.fetchall()
    return entries

  def pens(self, ver=0):
    ''' return contents of pens table as list 
        OR pens name if version given

        TODO add method to create new pens
    '''
    self.cursor.execute("""
SELECT ver, gplfile
FROM pens;""")
    pen = [row[1] for row in self.cursor.fetchall()]
    pen.insert(0, None)  # avoid zero-based list
    #self.pp.pprint(pen)
    if ver: return pen[ver]
    else:   return pen

'''
the
end
'''
