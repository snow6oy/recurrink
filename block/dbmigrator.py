import psycopg2
import pprint
#from block import Views, BlockData
#from block.data import Compass
#from cell import Palette

class Db2:

  BLOCKSZ = tuple()
  ''' access pattern
  INPUT params needed for searching and/or data for new records
  OUTPUT either nrc:0 and selected entries OR nrc:1+ and new entries
  '''
  def __init__(self):
    ''' target
    '''
    connection  = psycopg2.connect(dbname='recurrink2')
    connection.autocommit = True

    self.cursor = connection.cursor()
    self.pp     = pprint.PrettyPrinter(indent=2)

  ## class Model
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

  def inkpal(self, ver=0):
    ''' return contents of inkpal table as list 
        OR inkpal name if version given

        TODO add method to create new inkpal
    '''
    new_record_count = 0
    self.cursor.execute("""
SELECT ver, gplfile
FROM inkpal;""")
    inkpals = [row[1] for row in self.cursor.fetchall()]
    inkpals.insert(0, None)  # avoid zero-based list
    # self.pp.pprint(inkpals)
    if ver: return new_record_count, inkpals[ver]
    else:   return new_record_count, inkpals

  ## class Block
  def blocks(self, mid, blocks_v1=dict()):
    ''' attempt to retrieve with mid else add new rows from db v1 values
    
        pos = {(11, 11): ('x', None)}
    '''
    new_record_count = 0
    self.cursor.execute("""
SELECT *
FROM blocks
WHERE mid = %s;""", [mid])
    dbrows = self.cursor.fetchall()

    if len(dbrows) == 0: # add new entries
      for position, celltop in blocks_v1.items():
        success   = True
        p0, p1    = position
        pos_int   = f'{{ {p0}, {p1} }}'  # format postgres style
        cell, top = celltop
        try:
          self.cursor.execute("""
INSERT INTO blocks (mid, position, cell, top)
VALUES (%s, %s, %s, %s);""", (mid, pos_int, cell, top)
          )
        except psycopg2.errors.UniqueViolation:  # 23505 
          succss = False
        if success: continue
        else:       raise KeyError(f'{mid=} and {pos=} must be unique')
        new_record_count += 1
      blocks = blocks_v1
    else: 
      blocks = dict()
      for row in dbrows:
        key = tuple(row[1])
        blocks[key] = tuple(row[2:])
    return new_record_count, blocks

  def setBlocksize(self, positions):
    x = [p[0] for p in list(positions.keys())]
    y = [p[1] for p in list(positions.keys())]
    self.BLOCKSZ = (max(x) + 1, max(y) + 1)

  def emptyBlock(self):
    block = list(range(self.BLOCKSZ[1]))
    for x in block:
      row      = list(range(self.BLOCKSZ[0]))
      block[x] = row
    return block

  def positionBlock(self, positions, top=False):
    ''' make positions pretty for yaml
    '''
    self.setBlocksize(positions)
    i     = 1 if top else 0
    block = self.emptyBlock()
    for p in positions:
      x, y = p
      block[y][x] = positions[p][i]

    if top: # does this model have any cells with top?
      truth = list()
      for row in block:
        truth.append(all(t is None for t in row))
      if truth.count(True) == len(block): block = None
    return block

  def version(self, ver):
    ''' attempt to replace non-plottable palettes
    '''
    if ver < 8: # stop right there
      raise ValueError(f'palette conversion needed for {ver}')
    return ver - 7

  def pens(self, pens, ver):
    '''
1 8       uniball
2 9       copic
3 10      stabilo68
4 11      copicsketch
5 12      sharpie
6 13      staedtler
    '''
    new_record_count = 0
    new_ver          = self.version(ver)
    self.cursor.execute("""
SELECT count(*) 
FROM pens
WHERE ver = %s;""", [new_ver])
    pcount  = self.cursor.fetchone()[0]
    new_pen = tuple()
    #print(f'{ver=} {new_ver=} {pcount=}')

    for pen in pens:
      tmp     = list(pen)
      tmp[0]  = new_ver
      new_pen = tuple(tmp)
      if pcount == 0:
        #print(new_pen)
        try:
          self.cursor.execute("""
INSERT INTO pens (ver, fill, penam)
VALUES (%s, %s, %s);""", new_pen
          )
        except psycopg2.errors.UniqueViolation:  # 23505 
          raise KeyError(f'{ver=} and {fill=} must be unique')
        new_record_count += 1
    return new_record_count, new_pen

  def compass(self, mid, conf):
    ''' retrieve compass entries by mid, optionally add new
    '''
    new_record_count = 0
    entries          = self.compassRead(mid)

    if len(entries) == 0 and conf:
      return self.compassWrite(mid, conf, new_record_count)
    return new_record_count, entries

  def compassWrite(self, mid, conf, new_record_count):
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

  def compassConf(self): pass # TODO copy compass.conf code over

  def rinks(self, rinkid, mid=0, meta=list(), size=None, factor=None):
    new_record_count = 0
    self.cursor.execute("""
SELECT *
FROM rinks
WHERE rinkid = %s;""", [rinkid]
    )
    rinkdata = self.cursor.fetchone()
    if rinkdata: 
      return new_record_count, rinkdata
    elif mid and len(meta) == 3:
      ver, pubdate, created = meta
      ver = self.version(ver)
      self.cursor.execute("""
INSERT INTO rinks (rinkid, mid, ver, clen, factor, created, pubdate)
VALUES (%s, %s, %s, %s, %s, %s, %s);""",  
        (rinkid, mid, ver, size, factor, created, pubdate)
      )
      new_record_count = 1
      rinkdata         = tuple(
        [rinkid, mid, ver, size, factor, created, pubdate]
      )
    else:
      raise ValueError('cannot create rink without mid and meta')
    return new_record_count, rinkdata

  def geometry(self, rinkid, celldata=dict()):
    ''' record geom data keyed by rinkid, cell and layer
    '''
    new_record_count = 0
    geom             = self.geometryRead(rinkid)
    if geom:         return new_record_count, geom
    elif celldata:   return self.geometryWrite(rinkid, celldata)
    else:            raise ValueError(f'cannot find geometries for {rinkid}')

  def geometryWrite(self, rinkid, celldata):
    ''' create image layers as database rows
        FG is mandatory BG and TOP are optional
        see t.geometry for details
    '''
    new_record_count = 0
    geom             = dict()
    for label, cell in celldata.items():
      if label not in geom: geom[label] = list()
      name   = cell['shape']
      size   = cell['size']
      facing = cell['facing']

      if cell['bg']:
        self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 0, 'square', 'medium', 'C')
        )
        geom[label].append(tuple(['square', 'medium', 'C'])) # z 0

      z = len(geom[label])
      self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
        (rinkid, label, z, name, size, facing)
      )
      geom[label].append(tuple([name, size, facing])) # z 1

      if bool(cell['top']):
        z = len(geom[label])
        self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, z, name, size, facing)
        )
        geom[label].append(tuple([name, size, facing])) # assume top is last

      new_record_count += 1
    return new_record_count, geom

  def _geometryWrite(self, rinkid, celldata):
    new_record_count = 0
    geom             = dict()
    for label, cell in celldata.items():
      if label not in geom: geom[label] = list()
      name   = cell['shape']
      size   = cell['size']
      facing = cell['facing']
      if bool(cell['top']):
        self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 2, name, size, facing)
        )
        ######
        # Appending none works when label is unique
        # e.g. cell x only has top
        # But when label is both fg and top this may lead 
        # to data loss
        #####
        [geom[label].append(None) for empty in range(len(geom[label]), 2)]
        geom[label].append(tuple([name, size, facing])) # assume top is last
      else:
        self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 0, 'square', 'medium', 'C')
        )
        geom[label].append(tuple(['square', 'medium', 'C'])) # z 0
        self.cursor.execute("""
INSERT INTO geometry (rinkid, cell, layer, name, size, facing)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 1, name, size, facing)
        )
        geom[label].append(tuple([name, size, facing])) # z 1
      new_record_count += 1
    return new_record_count, geom

  def geometryRead(self, rinkid):
    ''' read geometry by rinkid
    '''
    geom = dict()
    self.cursor.execute("""  
SELECT *
FROM geometry
WHERE rinkid = %s;""", 
      [rinkid]   # implicit order by cell layer 
    )
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in geom: geom[label] = list()
      #[geom[label].append(None) for empty in range(len(geom[label]), z)]
      geom[label].insert(z, row[3:])
    return geom

  def strokes(self, rinkid, ver, celldata=dict()):
    new_record_count = 0
    ''' record stroke data, if any
    '''
    self.cursor.execute("""  
SELECT *
FROM strokes
WHERE rinkid = %s;""", 
      [rinkid] 
    )
    dbrows = self.cursor.fetchall()
    if dbrows: 
      strk = dict()
      for row in dbrows:
        label = row[1]
        z     = row[2]
        if label in strk:
          strk[label].insert(z, row[4:])
        else:
          strk[label] = list()
          strk[label].insert(0, tuple())  # background hack
          items = list(row[5:])
          items.insert(0, self.prettyHash(row[4], remove=True))
          strk[label].insert(z, items)
      return new_record_count, strk

    strk = dict()
    for label, cell in celldata.items():
      if 'stroke' in cell:
        fill      = cell['stroke']
        opacity   = cell['stroke_opacity']
        width     = cell['stroke_width']
        dasharray = cell['stroke_dasharray']
      else:
        continue
      if label not in strk: strk[label] = list()
      if bool(cell['top']):
        self.cursor.execute("""
INSERT INTO strokes (rinkid, cell, layer, ver, fill, opacity, width, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 2, ver, fill, opacity, width, dasharray)
        )
        strk[label].insert(2, tuple([ver, fill, opacity, width, dasharray])) 
      else:
        self.cursor.execute("""
INSERT INTO strokes (rinkid, cell, layer, ver, fill, opacity, width, dasharray)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 1, ver, fill, opacity, width, dasharray)
        )
        strk[label].insert(0, tuple())
        strk[label].insert(1, tuple([ver, fill, opacity, width, dasharray])) 
      new_record_count += 1
    return new_record_count, strk

  def prettyHash(self, val, remove=False):
    ''' YAML looks nicer with FF00CC but database wants #FF00CC
    '''
    if val is None:  # TODO or FFF ?
      return         # ignore empty background
    rgb = str(val) # rgb must be a string but YAML can send int
    fix = str()
    if remove:          fix = rgb[1:]
    elif rgb[0] == '#': fix = rgb
    else:               fix = '#' + str(rgb)
    return fix

  def palette(self, rinkid, ver, celldata=dict()):
    ''' read and write a block palette 
    '''
    palettes         = self.paletteRead(rinkid)
    if palettes:     return 0, palettes
    elif celldata:   return self.paletteWrite(rinkid, ver, celldata)
    else:            raise ValueError('not found {rinkid=}')

  def paletteRead(self, rinkid):
    ''' read palette by rinkid
    '''
    self.cursor.execute("""  
SELECT *
FROM palette
WHERE rinkid = %s;""", 
      [rinkid] 
    )
    pal = dict()
    for row in self.cursor.fetchall():
      label, z = row[1:3]
      if label not in pal: pal[label] = list()
      items      = list(row[5:])
      # fill in gaps
      #[pal[label].append(None) for _ in range(len(pal[label]), z)]
      items.insert(0, self.prettyHash(row[4], remove=True))
      pal[label].insert(z, tuple(items))
    return pal

  def paletteWrite(self, rinkid, ver, celldata):
    ''' write and return new entries
    '''
    new_record_count = 0
    pal              = dict()
    for label, cell in celldata.items():
      if label not in pal: pal[label] = list()
      fill      = cell['fill']
      opacity   = cell['fill_opacity']

      if cell['bg']:
        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 0, ver, cell['bg'], 1)
        )
        pal[label].insert(0, tuple([ver, cell['bg'], 1]))

      z = len(pal[label])
      self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
        (rinkid, label, z, ver, fill, opacity)
      )
      pal[label].insert(z, tuple([ver, fill, opacity])) 

      if bool(cell['top']):
        z = len(pal[label])
        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, z, ver, fill, opacity)
        )
        pal[label].insert(z, tuple([ver, fill, opacity])) 

      new_record_count += 1
    return new_record_count, pal

  def _paletteWrite(self, rinkid, ver, celldata):
    ''' write and return new entries
    '''
    new_record_count = 0
    pal              = dict()
    for label, cell in celldata.items():
      if label not in pal: pal[label] = list()
      fill      = cell['fill']
      opacity   = cell['fill_opacity']
      if bool(cell['top']):
        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          # ('2558c8da8ed39d47f50c36b9a7ae1531', 'g', 2, 4, '#d4aa00', 0.5)
          (rinkid, label, 2, ver, fill, opacity)
        )
        [pal[label].append(None) for _ in range(len(pal[label]), 2)]
        pal[label].insert(2, tuple([ver, fill, opacity])) 
      else:
        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 0, ver, cell['bg'], 1)
        )
        pal[label].insert(0, tuple([ver, cell['bg'], 1]))
        self.cursor.execute("""
INSERT INTO palette (rinkid, cell, layer, ver, fill, opacity)
VALUES (%s, %s, %s, %s, %s, %s);""",
          (rinkid, label, 1, ver, fill, opacity)
        )
        pal[label].insert(1, tuple([ver, fill, opacity])) 
      new_record_count += 1
    return new_record_count, pal

  def rinkMeta(self, rinkdata):
    ''' gather metadata from db to write conf/MODEL.yaml
    '''
    nrc, model    = self.model(mid=rinkdata[1])
    print(f'{nrc} new model(s)') if nrc else print(f'got {model=}')
    nrc, pos      = self.blocks(mid=rinkdata[1])
    print(f'{nrc} new block(s)') if nrc else print(f'got {len(pos)=}')
    nrc, inkpal   = self.inkpal(ver=rinkdata[2])
    print(f'{nrc} new inkpal') if nrc else print(f'got {inkpal=}')

    metadata = {
      'id': rinkdata[0],
      'model': model,
      'palette': inkpal
    }
    fgpos = self.positionBlock(pos)
    topos = self.positionBlock(pos, top=True)
    metadata['positions'] = { 'foreground': fgpos }
    if topos: metadata['positions']['top'] = topos
 
    return model, metadata

  def cellData(self, rinkdata):
    ''' gather celldata from db to write conf/MODEL.yaml
    '''
    rinkid        = rinkdata[0]
    nrc, geom     = self.geometry(rinkid)
    print(f'{nrc} new geom') if nrc else print(f'got {len(geom)=}')
    nrc, stk      = self.strokes(rinkid, rinkdata[2])
    print(f'{nrc} new strokes') if nrc else print(f'got {len(stk)=}')
    nrc, pal      = self.palette(rinkid, rinkdata[2])
    print(f'{nrc} new palettes') if nrc else print(f'got {len(pal)=}')
    self.pp.pprint(pal)

    celldata      = dict()
    ######################
    for label in geom:
      #print(f'{label=} {len(geom[label])}')
      g = dict(zip(['name', 'size', 'facing'], geom[label][-1]))
      z = len(geom[label]) 
      g['top'] = True if z == 3 else False
      p  = dict(zip(['fill', 'opacity'], pal[label][-1]))
      p['background'] = pal[label][0][0] if z > 1 else None

      if label in stk: 
        s = dict(zip(['fill', 'opacity', 'width', 'dasharray'], stk[label][1]))
        celldata[label] = {
          'geom': g,
        'stroke': s,
         'color': p
        }
      else: 
        celldata[label] = { 'geom': g, 'color': p }
    nrc, rinkdata = self.rinks(rinkid)
    print(f'{nrc} new rink(s)') if nrc else print(f'got {len(rinkdata)=}')
    '''
    self.pp.pprint(pos)
    self.pp.pprint(rinkdata)
    self.pp.pprint(celldata)
    '''
    return celldata

  def __cellData(self, rinkdata):
    ''' gather celldata from db to write conf/MODEL.yaml
    '''
    rinkid        = rinkdata[0]
    nrc, geom     = self.geometry(rinkid)
    print(f'{nrc} new geom') if nrc else print(f'got {len(geom)=}')
    nrc, stk      = self.strokes(rinkid, rinkdata[2])
    print(f'{nrc} new strokes') if nrc else print(f'got {len(stk)=}')
    nrc, pal      = self.palette(rinkid, rinkdata[2])
    print(f'{nrc} new palettes') if nrc else print(f'got {len(pal)=}')

    celldata      = dict()
    ######################
    for label in geom:
      #print(f'{label=} {len(geom[label])}')
      if len(geom[label]) == 2: 
        g             = dict(zip(['name', 'size', 'facing'], geom[label][1]))
        g['top']      = False
        p               = dict(zip(['fill', 'opacity'], pal[label][1]))
        p['background'] = pal[label][0][0]
      elif len(geom[label]) == 3: # for when top is true 
        g             = dict(zip(['name', 'size', 'facing'], geom[label][2]))
        g['top']      = True
        p               = dict(zip(['fill', 'opacity'], pal[label][2]))
        p['background'] = None
      if label in stk: 
        s = dict(zip(['fill', 'opacity', 'width', 'dasharray'], stk[label][1])) 
        celldata[label] = {
          'geom': g,
        'stroke': s,
         'color': p
        }
      else: 
        celldata[label] = { 'geom': g, 'color': p }
    nrc, rinkdata = self.rinks(rinkid)
    print(f'{nrc} new rink(s)') if nrc else print(f'got {len(rinkdata)=}')
    '''
    self.pp.pprint(pos)
    self.pp.pprint(rinkdata)
    self.pp.pprint(celldata)
    '''
    return celldata
