import random
import pprint
#import psycopg2
from config import Db2

class ModelData(Db2):
  ''' class methods give access to models, blocks, compass and pens table
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self): 
    self.count = 0
    super().__init__()

  def model(self, name=None, mid=0):
    ''' retrieve or create and retrieve a model id from a name
        OR given a model ID, retrieve a name
        given neither, return a list of models
    '''
    models           = self.modelRead()
    if name in models: found = models.index(name) # ID or 0 if name is None
    else:              found = False

    if found:  return found
    elif name: return self.modelWrite(name) 
    elif mid:  return models[mid]
    else:      return models

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
    self.count = 0
    self.cursor.execute("""
INSERT INTO models (mid, model)
VALUES (DEFAULT, %s)
RETURNING mid;""", [name])
    mid = self.cursor.fetchone()
    self.count = 1
    return mid[0]

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
    self.count = 0

    for position, celltop in blocks.items():
      p0, p1    = position
      pos_int   = f'{{ {p0}, {p1} }}'  # format postgres style
      cell, top = celltop
      self.cursor.execute("""
INSERT INTO blocks (mid, position, cell, top)
VALUES (%s, %s, %s, %s);""", (mid, pos_int, cell, top)
      )
      self.count += 1
    return blocks

  def compass(self, mid, conf=None):
    ''' retrieve compass entries by mid, optionally add new
    '''
    entries = self.compassRead(mid)
    if len(entries):          return 0, entries
    elif conf and len(conf):  return self.compassWrite(mid, conf)
    else:                     return 0, None

  def compassWrite(self, mid, conf):
    self.count = 0
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
      self.count += 1
    return entries

  def compassRead(self, mid):
    self.cursor.execute("""
SELECT *
FROM compass
WHERE mid = %s;""", [mid])
    entries = self.cursor.fetchall()
    return entries

  def pens(self, ver=None):
    ''' return contents of pens table as list 
        OR pens name if version given

        TODO add method to create new pens
    '''
    self.cursor.execute("""
SELECT ver, gplfile
FROM pens;""")
    pen = [row[1] for row in self.cursor.fetchall()]
    #pen.insert(0, None)  # avoid zero-based list
    #self.pp.pprint(pen)
    if ver == 0: return None
    elif ver   : return pen[ver]
    else       : return pen

  def setBlocksize(self, mid):
    self.cursor.execute("""
SELECT position
FROM blocks
WHERE mid = %s;""", [mid])
    positions = self.cursor.fetchall()
    x = [p[0][0] for p in positions]
    y = [p[0][1] for p in positions]
    return (max(x) + 1, max(y) + 1)

  def positions(self, mid):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
    '''
    (bsX, bsY) = self.setBlocksize(mid)
    data = [[0 for x in range(bsX)] for y in range(bsY)]
    self.cursor.execute("""
SELECT position, cell 
FROM blocks 
WHERE mid = %s;""", [mid])
    records = self.cursor.fetchall()
    for r in records:
      x = r[0][1] # x is the inner array
      y = r[0][0]
      data[x][y] = r[1]
    return data

  # list_model_with_stats
  def stats(self):
    ''' display uniq cells, blocksize and model names
    '''
    stats = dict()
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for row in self.cursor.fetchall():
      model, uniq, size = row
      stats[model] = list()
      stats[model].append(uniq)
      stats[model].append(size)
    self.cursor.execute("""
SELECT model, count(top) 
FROM blocks
GROUP BY model;""",)
    top = self.cursor.fetchall()
    model = 'soleares'
    self.cursor.execute("""
SELECT model, count(cell) 
FROM compass
GROUP BY model;""",)
    compass = self.cursor.fetchall()
    for m in stats:
      n = [t for t in top if t[0] == m]
      stats[m].append(n[0][1]) # assume blocks always have model
      i = [c for c in compass if c[0] == m] # but compass does not, so set a default
      counter = i[0][1] if len(i) else 0
      stats[m].append(counter)
    output = f"uniq\t   x\t   y\t top\tcompass\t model\n" + ('-' * 80) + "\n"
    for m in stats:
      output += f"{stats[m][0]:>4}\t{stats[m][1][0]:>4}\t{stats[m][1][1]:>4}\t{stats[m][2]:>4}\t{stats[m][3]:>4}\t{m}\n"
    return output

'''
the
end
'''

