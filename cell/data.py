import pprint
from .transform import Transform

class CellData(Transform):
  ''' use-cases

CELL    FG  BG  TOP BG
a       y   n   n   n
b       y   y   n   n
c       y   y   y   n
d       n   n   y   y
e       y   n   y   n

TOP has two versions of truth
it is definetly True when a cell position
has both FG and TOP allocated

cells that are marked as TOP but
are uniquely allocated to a position without a FG (e.g. cell d)
are also TOP.
These will be allocated a BG as if they were a FG
but they will NOT be allocated a Top layer

Expected result

cell  z    BGs
--------------------
a     0    n
a     1    y
b     0    y
b     1    y
c     0    y
c     1    y
c     2    y
d     0    y
d     1    y
e     0    n
e     1    y
e     2    y
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.count = 0
    super().__init__()

  def layers(self, rinkid, celldata=dict()):
    ''' each layer has a db record keyed by rinkid, cell and layer
    '''
    data = self.layersRead(rinkid)
    if data and celldata: 
      self.layersUpdate(rinkid, celldata)
    elif celldata:   
      self.layersWrite(rinkid, celldata)
    elif data:
      return data
    else:
      raise ValueError(f'cannot find any layer for {rinkid}')

  def _layers(self, rinkid, celldata=dict()):
    ''' each layer has a db record keyed by rinkid, cell and layer
    '''
    data             = self.layersRead(rinkid)
    if data:         return data
    elif celldata:   return self.layersWrite(rinkid, celldata)
    else:            raise ValueError(f'cannot find any layer for {rinkid}')

  def layersRead(self, rinkid):
    ''' read layers by rinkid
    '''
    data = dict()
    self.cursor.execute("""  
SELECT *
FROM layers
WHERE rinkid = %s
ORDER BY cell, layer;""", 
      [rinkid]   # order by cell layer 
    )
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in data: data[label] = list()
      has_content = [True for x in row[3:] if x] # test for empty strings
      if has_content:
        data[label].insert(z, row[3:])
      else:
        data[label].insert(z, tuple())
    return data

  def layersWrite(self, rinkid, celldata=dict()):
    ''' move this to block.data ?
    '''
    self.count = 0 # reset new record counter
    for label, cell in celldata.items():
      self.cellWrite(rinkid, label, cell)

  def cellWrite(self, rinkid, label, cell):
    ''' write cell to layers table
    '''
    for z, row in enumerate(cell): 
      if len(row) < 5 and z ==0:
        row = tuple([None] * 5)
      if len(row) != 5:
        print(f'cannot write {row} because not 5')
        continue
      ''' print(f'{label=} {z} {row}')
      '''
      self.cursor.execute("""
INSERT INTO layers (rinkid, cell, layer, name, size, facing, stroke, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (rinkid, label, z) + row
      )
      self.count += 1

  def _layersWrite(self, rinkid, celldata=dict()):
    self.count = 0 # reset new record counter

    for label, cell in celldata.items():
      for z, row in enumerate(cell): 
        if len(row) < 5 and z ==0:
          row = tuple([None] * 5)
        if len(row) != 5:
          print(f'cannot write {row} because not 5')
          continue
        self.cursor.execute("""
INSERT INTO layers (rinkid, cell, layer, name, size, facing, stroke, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (rinkid, label, z) + row
        )
        self.count += 1

  def layersUpdate(self, rinkid, celldata):
    ''' layers are immutable except for color swaps
    '''
    self.count = 0
    for label, cell in celldata.items():
      for z, row in enumerate(cell):
        if len(row):
          self.cursor.execute("""
UPDATE layers
SET stroke   = %s
WHERE rinkid = %s
AND cell     = %s
AND layer    = %s;""", (row[3], rinkid, label, z)
          )
          self.count += 1
    #print(f'{self.count=}')

  ''' record geom data keyed by rinkid, cell and layer
  '''
  def _geometry(self, rinkid, celldata=dict()):
    new_record_count = 0
    geom             = self.geometryRead(rinkid)
    if geom:         return new_record_count, geom
    elif celldata:   return self.geometryWrite(rinkid, celldata)
    else:            raise ValueError(f'cannot find geometries for {rinkid}')

  ''' create cell layers as database rows
        BG and FG are mandatory. TOP is optional

        Empty backgrounds are saved with metadata and null values
        Because omitting the entry altogether makes layering indeterminate

        see t.geometry for details
  '''
  def _geometryWrite(self, rinkid, celldata):
    new_record_count = 0
    #celldata         = self.dataV1(celldata) # convert v1 to layered format
    #celldata         = self.dataV2(celldata) # convert v1 to layered format

    for label, cell in celldata.items():
      for z, layer in enumerate(cell):
        if len(layer):
          name, size, facing = layer[:3]
          self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
            (rinkid, label, z, name, size, facing)
          )
          #print(rinkid, label, z, name, size, facing)
        elif z == 0:
          self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
            (rinkid, label, z, None, None, None)
          )
          #print(rinkid, label, z, name, size, facing)
        else:
          raise ValueError('can only make assumptions in background layer')
        new_record_count += 1
    return new_record_count, celldata

  ''' read geometry by rinkid
  '''
  def _geometryRead(self, rinkid):
    geom = dict()
    self.cursor.execute("""  
SELECT *
FROM geometry
WHERE rinkid = %s
ORDER BY cell, layer;""", 
      [rinkid]   # implicit order by cell layer 
    )
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in geom: geom[label] = list()
      has_content = [True for x in row[3:] if x] # test for empty strings
      if has_content:
        geom[label].insert(z, row[3:])
      else:
        geom[label].insert(z, tuple())
    return geom


  def _palette(self, rinkid, ver, celldata=dict()):
    ''' read and write a block palette 
    '''
    palettes         = self.paletteRead(rinkid)
    if palettes:     return 0, palettes
    elif celldata:   return self.paletteWrite(rinkid, ver, celldata)
    else:            raise ValueError('not found {rinkid=}')

  def _paletteRead(self, rinkid):
    ''' read palette by rinkid
 
        TODO prettify hash in TmpFile
    '''
    self.cursor.execute("""  
SELECT *
FROM palette
WHERE rinkid = %s
ORDER BY cell, layer;""", 
      [rinkid] 
    )
    pal = dict()
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in pal: pal[label] = list()
      pal[label].append(row[4:])
    return pal

  def _paletteWrite(self, rinkid, ver, celldata):
    ''' write new entries in palette table
    '''
    new_record_count = 0
    #celldata         = self.dataV1(celldata) # convert v1 to layered format

    for label, cell in celldata.items():
      for z, layer in enumerate(cell):
        if len(layer):
          fill, opacity = layer[3:5]
        elif z == 0: # no bg
          fill, opacity = None, None
        else:
          raise ValueError(f'palette got an empty layer {label}')

        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, z, ver, fill, opacity)
        )
        new_record_count += 1
    return new_record_count, celldata

  def _strokes(self, rinkid, ver, celldata=dict()):
    strokes         = self.strokeRead(rinkid)
    if strokes:     return 0, strokes
    elif celldata:  return self.strokeWrite(rinkid, ver, celldata)
    else:           raise ValueError('not found {rinkid=}')

  def _strokeRead(self, rinkid):
    self.cursor.execute("""  
SELECT *
FROM strokes
WHERE rinkid = %s;""", 
      [rinkid] 
    )
    sk = dict()
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in sk: sk[label] = list()
      sk[label].append(row[4:])
    return sk

  def _strokeWrite(self, rinkid, ver, celldata):
    ''' record stroke data, if any
    '''
    new_record_count = 0
    #celldata         = self.dataV1(celldata)
    for label, cell in celldata.items():
      for z, layer in enumerate(cell):
        if z and len(layer) == 9:
          fill, opacity, width, dasharray = layer[5:]
        else: # either is background or stroke width is zero
          fill, opacity, width, dasharray = None, None, None, None

        self.cursor.execute("""
INSERT INTO strokes (rinkid, cell, layer, ver, fill, opacity, width, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
          (rinkid, label, z, ver, fill, opacity, width, dasharray)
        )
        # print(fill, opacity, width, dasharray)
        new_record_count += 1
    return new_record_count, celldata

'''
the
end
'''
