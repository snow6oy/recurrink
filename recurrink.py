#!/usr/bin/env python3

''' sudo apt-get install python3-psycopg2 
'''
import sys
import psycopg2
import pprint
import getopt
import random
pp = pprint.PrettyPrinter(indent=2)
from builder import Builder

class Db(Builder):

  def __init__(self, model, machine=False):
    # Create connection to postgres
    connection = psycopg2.connect(dbname='recurrink')
    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    self.cursor = connection.cursor()
    super().__init__(model, machine=machine)

  def load_model(self):
    ''' load csv data as 2D array
      ./recurrink.py -m soleares -o CELL
      [['a', 'b', 'a'], ['c', 'd', 'c']]
    '''
    self.cursor.execute("""
SELECT blocksizeXY
FROM models
WHERE model = %s;""", [self.model])
    (bsX, bsY) = self.cursor.fetchone()[0]
    data = [[0 for x in range(bsX)] for y in range(bsY)]
    self.cursor.execute("""
SELECT position, cell 
FROM blocks 
WHERE model = %s;""", [self.model])
    records = self.cursor.fetchall()
    for r in records:
      x = r[0][1] # x is the inner array
      y = r[0][0]
      data[x][y] = r[1]
    return data

  def list_model(self):
    self.cursor.execute("""
SELECT model
FROM models;""", )
    records = [m[0] for m in self.cursor.fetchall()]
    return records

  def list_model_with_stats(self):
    ''' display uniq cells, blocksize and model names
    '''
    output = f"uniq    x    y model\n" + ('-' * 80) + "\n"
    self.cursor.execute("""
SELECT model, uniqcells, blocksizexy
FROM models;""",)
    for m in self.cursor.fetchall():
      output += f"{m[1]:>4} {m[2][0]:>4} {m[2][1]:>4} {m[0]}\n"
    return output

  def load_view(self, view):
    ''' view is currently /tmp/MODEL.json but here we expect view to be a digest. e.g.
      ./recurrink.py -m soleares --output RINK --view e4681aa9b7aef66efc6290f320b43e55 '''
    header = [
      'cell','shape','shape_size','shape_facing','top','fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]
    data = dict()
    self.cursor.execute("""
SELECT cell, shape, size, facing, top, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM views, styles, geometry
WHERE views.sid = styles.sid
AND views.gid = geometry.gid
AND view = %s;""", [view])
    for cellvals in self.cursor.fetchall():
      z = zip(header, cellvals)
      d = dict(z)
      cell = d['cell']
      del d['cell']         # bit of a tongue twister that one :-D
      data[cell] = d
    return data

  def write_jsonfile(self, view=None, author='human'):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    csvdata = self.read_tmp_csvfile()
    (model, cellvalues, jsondata) = self.convert_row2cell(csvdata)
    update = False
    if model != self.model:
      raise ValueError(f"collision in /tmp {model} is not {self.model}")
    if view is None:   
      view = self.get_digest(cellvalues)

    for cell in jsondata:
      items = list(jsondata[cell].values())
      # re-order top print(type(top), top)
      top = items.pop()
      items.insert(5, bool(top)) 
      # ignore first 2 items cell and model
      gid = self.set_geometry(items[2:])
      sid = self.set_styles(items[2:])
      # UPSERT the view table
      try:
        self.cursor.execute("""
INSERT INTO views (view, cell, model, author, sid, gid)
VALUES (%s, %s, %s, %s, %s, %s);""", [view, cell, self.model, author, sid, gid])
      except psycopg2.errors.UniqueViolation:  # 23505 
        update = True
        self.cursor.execute("""
UPDATE views SET
author=%s, sid=%s, gid=%s
WHERE view=%s
AND cell=%s;""", [author, sid, gid, view, cell])
      digest = view
    return digest

  def set_geometry(self, items):
    ''' if first attempt at insert fails then fallback to select
        a side-effect is that PK increments each time. but does it matter?
    '''
    gid = None
    try:
      self.cursor.execute("""
INSERT INTO geometry (gid, shape, size, facing, top)
VALUES (DEFAULT, %s, %s, %s, %s)
RETURNING gid;""", items[:4])
      gid = self.cursor.fetchone()[0]
    except psycopg2.errors.UniqueViolation:  # 23505 
      self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s;""", items[:3])  # ignore top
      gid = self.cursor.fetchone()[0]
    return gid

  def set_styles(self, items):
    ''' just add style, no worry about duplicates
        ['#fff', '#ccc', '1.0', '#000', 0, 0, '1.0']
    '''
    self.cursor.execute("""
INSERT INTO styles (sid, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
RETURNING sid;""", items[4:])
    return self.cursor.fetchone()[0]

  def uniq_cells(self):
    ''' send mondrian the robot a list of uniq cells 
    '''
    self.cursor.execute("""
SELECT DISTINCT(cell)
FROM blocks 
WHERE model = %s;""", [self.model])
    cells = [c[0] for c in self.cursor.fetchall()]
    return cells

  def load_rinkdata(self, view):
    ''' unpack the model(s) into a json database 
    '''
    model_data = self.load_model()
    json_data = self.load_view(view)
    if (len(json_data.keys()) != len(self.uniq)):
      raise KeyError(f"missing cells: {view}")

    return {
        'id': self.model,
        'size': (len(model_data[0]), len(model_data)),
        'cells': self.get_cells(model_data, json_data)
    }

###############################################################################
def usage():
  message = '''
-r random model name
-l list models
-m MODEL --output CSV  [--random]
-m MODEL --output JSON [--random]
-m MODEL --output RINK [--view VIEW]
-m MODEL --output CELL
-m MODEL --cell CELL
'''
  print(message)

def inputs():
  ''' get inputs from command line
  '''
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:o:c:v:lr", ["model=", "output=", "cell=", "view=", "list", "random"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  (model, output, cell, view, ls, rnd) = (None, None, None, None, False, False)
  for opt, arg in opts:
    if opt in ("-o", "--output") and arg in ('RINK', 'CSV', 'JSON', 'CELL', 'SVG'):
      output = arg
    elif opt in ("-c", "--cell"):
      cell = arg
    elif opt in ("-v", "--view"):
      view = arg
    elif opt in ("-m", "--model"):
      model = arg
    elif opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-l", "--list"):
      ls = True
    elif opt in ("-r", "--random"):
      rnd = True
    else:
      assert False, "unhandled option"
  return (model, output, cell, view, ls, rnd)

if __name__ == '__main__':
  (model, output, cell, view, ls, rnd) = inputs()
  ''''''''''''''''''''''''''''''''''''''''''
  db = Db(model, machine=rnd)
  if model:
    if output == 'CSV':                   # create tmp csv file containing a collection of random cell values
      print(db.write_csvfile())            # OR default vals for humans. return cell vals a b c d
    elif view and output == 'RINK':       # write RINK with Library json as source
      db.write_rinkfile(json_file=view)
    elif output == 'RINK':                # write RINK with MODEL.json as source
      print("deprecated, try with --view instead")
      #db.write_rinkfile()
    elif output == 'JSON':                # convert tmp csv into json as permanent record 
      print(db.write_jsonfile())          # write csvdata into views table and return digest
    elif output == 'CELL':                # get a list of uniq cells
      print(' '.join(db.uniq)) 
    elif cell:                            # lookup values by cell return as comma-separated string '1,square,north'
      print(db.get_cellvalues(cell)) 
    else:
      usage()
  elif ls:
    print(db.list_model_with_stats())     # for CLI user to get model summary from db
  elif rnd:
    print(random.choice(db.list_model())) # for mondrian to pluck a rando
  elif view and output == 'JSON':         # query db
    print("deprecated, try SVG instead")
  elif view and output == 'SVG':          # lookup SVG
    print(b.find_recurrence(view, 'svg')[0])
  else:
    usage()
