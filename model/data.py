import random
import psycopg2
from config import Db

class ModelData(Db):
  ''' models give us the base template to draw a rink
  '''
  def __init__(self): 
    super().__init__()

  def create(self, model, uniqcells, blocksizexy, scale):
    ''' only used once during The Great Import from JSON
    '''
    success = True
    try:
      self.cursor.execute("""
INSERT INTO models (model, uniqcells, blocksizexy, scale)
VALUES (%s, %s, %s, %s);""", [model, uniqcells, blocksizexy, scale])
    except psycopg2.errors.UniqueViolation:  # 23505 
      success = False
    return success

  def read(self, model=None):
    ''' fetch a single entry indexed by model 
        return a tuple
    '''
    if model:
      self.cursor.execute("""
SELECT *
FROM models
WHERE model = %s;""", [model])
      entry = self.cursor.fetchone()
      if entry:
        return entry
      else:
        raise ValueError(f"nothing found for {model}")
    else:
      self.cursor.execute("""
SELECT model
FROM models;""", )
      records = [m[0] for m in self.cursor.fetchall()]
      return records

  # TODO strip testcard out of the list
  def generate(self):
    models = self.read()
    return random.choice(models)

  def positions(self, model):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
      represented as a string
    '''
    self.cursor.execute("""
SELECT blocksizeXY
FROM models
WHERE model = %s;""", [model])
    (bsX, bsY) = self.cursor.fetchone()[0]
    data = [[0 for x in range(bsX)] for y in range(bsY)]
    self.cursor.execute("""
SELECT position, cell 
FROM blocks 
WHERE model = %s;""", [model])
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

  def getScale(self, model):
    return self.read(model=model)[3]

'''
  the
  end
'''
