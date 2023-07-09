import psycopg2
import glob
from os import path, sep
connection = psycopg2.connect(dbname='recurrink')
connection.autocommit = True  # Ensure data is added to the database immediately after write commands
c = connection.cursor()
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def add(globex):
  files = glob.glob(globex)
  unseen = []
  for f in files:
    p = path.splitext(f)[0]
    _, model, view = p.split(sep)
    #print(view, model)
    try:
      c.execute("""
INSERT INTO files (view, model)
VALUES (%s, %s);""", [view, model])
      unseen.append(view)
    except psycopg2.errors.UniqueViolation:  # 23505 
      pass
  #print(unseen)
  return len(unseen)

def count_views():
  ''' which db entries do not have a corresponding SVG on the filesystem
  '''
  c.execute("""
SELECT v.view, v.model
FROM views v
LEFT JOIN files f ON f.view = v.view
WHERE f.view IS NULL""")
  found = c.fetchall()
  return found

def count_files():
  ''' which files do not have a corresponding entry in the db
  '''
  c.execute("""
SELECT f.view, f.model
FROM files f
LEFT JOIN views v ON v.view = f.view
WHERE v.view IS NULL""")
  found = c.fetchall()
  return found

'''
fcount = add('rinks/*/*.svg')
print(f"{fcount} files inserted")
views = count_views()
[print(f"{v[0]} {v[1]}") for v in views]
print()
print(f"{len(views)} views without files")
print()
'''
files = count_files()
[print(f"{f[0]} {f[1]}") for f in files]
print()
print(f"{len(files)} files without views")
