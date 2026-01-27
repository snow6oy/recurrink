import pprint
from .transform import Transform

class CellData2(Transform):

  def __init__(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    super().__init__()

  def geometry(self, rinkid, celldata=dict()):
    ''' record geom data keyed by rinkid, cell and layer
    '''
    new_record_count = 0
    geom             = self.geometryRead(rinkid)
    if geom:         return new_record_count, geom
    elif celldata:   return self.geometryWrite(rinkid, celldata)
    else:            raise ValueError(f'cannot find geometries for {rinkid}')

  def geometryRead(self, rinkid):
    ''' read geometry by rinkid
    '''
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

  def geometryWrite(self, rinkid, celldata):
    ''' create cell layers as database rows
        BG and FG are mandatory. TOP is optional

        Empty backgrounds are saved with metadata and null values
        Because omitting the entry altogether makes layering indeterminate

        see t.geometry for details
    '''
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

  def palette(self, rinkid, ver, celldata=dict()):
    ''' read and write a block palette 
    '''
    palettes         = self.paletteRead(rinkid)
    if palettes:     return 0, palettes
    elif celldata:   return self.paletteWrite(rinkid, ver, celldata)
    else:            raise ValueError('not found {rinkid=}')

  def paletteRead(self, rinkid):
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

  def paletteWrite(self, rinkid, ver, celldata):
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

  def strokes(self, rinkid, ver, celldata=dict()):
    strokes         = self.strokeRead(rinkid)
    if strokes:     return 0, strokes
    elif celldata:  return self.strokeWrite(rinkid, ver, celldata)
    else:           raise ValueError('not found {rinkid=}')

  def strokeRead(self, rinkid):
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

  def strokeWrite(self, rinkid, ver, celldata):
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
