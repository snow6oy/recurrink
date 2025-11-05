import pprint
import psycopg2
from config import *
from .shape import *

class Geometry(Db):
  ''' Generate a geometry by selecting existing geometries from db
      Validate input geometries
  '''
  def __init__(self):
    super().__init__()
    self.attributes = {
      'shape': ['circle', 'line', 'square', 'triangl', 'diamond'],
      'facing': ['C','N', 'S', 'E', 'W'],
      'size': ['medium', 'large'],
      'top': [True, False]
    }
    self.flip = {
       'E': { 'N': 'S', 'S': 'N' },
       'N': { 'W': 'E', 'E': 'W' },
      'NE': { 'N': 'E', 'E': 'N' },
      'SW': { 'S': 'W', 'W': 'S' }
    }
    self.defaults = { 
      'shape':'square', 'size':'medium', 'facing':None, 'top':False 
    }

  def create(self, items):
    ''' there are finite permutation of geometries so stopped random creation
        also because psycopg2.errors.UniqueViolation # 23505 consumes SERIAL
    '''
    pass

  #def read(self, top=None, gid=None, item=list()):
  def read(self, top=None, gid=None):
    ''' always returns a list, even if only one member (gid)
    '''
    items = list()
    if gid:  
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE gid = %s;""", [gid])
      items = self.cursor.fetchone()
    elif isinstance(top, bool):
      pass # self.load()
      self.cursor.execute("""
SELECT shape, size, facing, top
FROM geometry
WHERE top = %s;""", [top])
      items = self.cursor.fetchall()
    return items

  def read_gid(self, geom):
    ''' in order to commit, the item must be converted to a gid
    '''
    item = [geom[k] for k in ['name', 'size', 'facing', 'top']]
    self.cursor.execute("""
SELECT gid
FROM geometry
WHERE shape = %s
AND size = %s
AND facing = %s
AND top = %s;""", item)
    gid = self.cursor.fetchone()
    if gid is None: # add new geometry
      raise ValueError(f"not expecting to find a new geom {item}")
    return gid[0]

  def read_one(self, flip):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE facing = %s
OR facing = %s
ORDER BY random() LIMIT 1;""", flip)
    return list(self.cursor.fetchone())

  def read_all(self, top):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE facing = 'C'
AND top = %s
ORDER BY random() LIMIT 1;""", [top])
    return self.cursor.fetchone()

  def read_any(self, top):
    self.cursor.execute("""
SELECT shape, size, facing, top 
FROM geometry 
WHERE top = %s
ORDER BY random() LIMIT 1;""", [top])
    return list(self.cursor.fetchone())

  def generate_any(self, top=False):
    ''' randomly select a db entry filtered on top
    '''
    return dict(zip(['shape','size','facing','top'], Geometry.read_any(self, top)))

  def generate_all(self, top=False):
    return dict(zip(['shape','size','facing','top'], self.read_all(top)))

  def generate_one(self, axis, top, facing=None):
    ''' use the compass and pair cells along the axis
    '''
    flip = self.flip[axis]
    geom = self.read_one(list(flip.keys()))
    # makes western line and IT IS FINE
    geom[2] = flip[facing] if facing else geom[2] 
    geom[3] = top
    return dict(zip(['shape','size','facing','top'], geom))

  def validate(self, label, geom):
    if 'name' in geom: name = geom['name']
    else: raise ValueError(f"validation error: {label}")

    shapes = {
         'line': Rectangle(name),
         'edge': Rectangle(name),
       'square': Rectangle(name),
       'sqring': Rectangle(name),
       'gnomon': Gnomon(),
      'parabol': Parabola(),
      'triangl': Triangle(),
      'diamond': Diamond(),
       'circle': Circle()
    }
    shape  = shapes[name]
    errmsg = shape.validate(geom)
    if errmsg: raise ValueError(f"validation error {label}: {name} {errmsg}")
'''
the
end
'''
