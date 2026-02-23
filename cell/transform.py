import psycopg2
import pprint
from decimal import *
from config import Db2

class Transform(Db2):

  ''' generic functions to convert celldata to cellrows and back again

      Formats

      YAML celldata nested into Geom Palette Stroke
      DBV1 celldata flat from db1 
      SVG  celldata order by Layer with unique styles
      DBV2 cellrows aligned to db2 schema
      DBV3 cellrows for revised db2 schema
      YAM3 celldata flat with style for plotter

      Transformations

      import export  use-case
      ----------------------- deprecated
               DBV1   DBV2    
      dataV2   YAML   DBV2    
    txDbv2Dbv3 DBV2   DBV3
               DBV1   YAML    ?
      ----------------------- done
      dataV1   DBV1   DBV3    migration to be deprecated once dbv1 is sunset
      dataV3   YAML   DBV3    compatibility
    txDbv3Yaml DBV3   YAML    backwards compatibiliy until DBV3 is rolled out
      ----------------------- future
               Y3ML   DBV3    write new rinks
               DBV3   Y3ML    
               DBV3   SVG    

      TODO align with Block Cell model block/transform > cell/transform
  '''
  def dataV1(self, celldata):
    ''' create layered data structure
        BG and FG are mandatory TOP is optional
        see t.geometry for use cases
    '''
    data = dict()
    for label, cell in celldata.items():
      #print(f'dataV1 {label=} {cell}')
      if label not in data: data[label] = list()
      if 'stroke_width' in cell and cell['stroke_width'] > 0:
        dasharray = cell['stroke_dasharray']
      else:
        dasharray = 0

      bg  = cell['bg']
      row = [
        cell['shape'],
        cell['size'],
        cell['facing'],
        cell['fill'],
        dasharray
      ]

      if bg:
        data[label].append(tuple(['square', 'medium', 'C', bg, 1])) # z 0
      else:
        data[label].append(tuple())

      data[label].append(tuple(row)) # z 1

      if bool(cell['top']): # z 2
        data[label].append(tuple(row))

    return data

  def dataV2(self, celldata):
    ''' convert nested dict into cellrows for db ops
    '''
    data = dict()
    for label, cell in celldata.items():
      if label not in data: data[label] = list()
      if 'stroke' in cell and cell['stroke']:
        dasharray = cell['stroke']['dasharray']
      else:
        dasharray = 0
      bg = cell['color']['background']

      row = [
        cell['geom']['name'],
        cell['geom']['size'],
        cell['geom']['facing'],
        cell['color']['fill'],
        dasharray
      ]
      '''
        row += [
          cell['stroke']['fill'],
          cell['stroke']['opacity'],
          cell['stroke']['width'],
         ]
      '''
      if bg:
        data[label].append(tuple(['square', 'medium', 'C', bg, 1])) # z 0
      else:
        data[label].append(tuple())
      data[label].append(tuple(row)) # z 1

      if bool(cell['geom']['top']): # z 2
        data[label].append(tuple(row))

    return data

  def dataV3(self, celldata):
    ''' convert nested dict into cellrows for db ops
    '''
    data = dict()
    for label, cell in celldata.items():
      if label not in data: data[label] = list()

      fill_bg, fill_fg  = cell['color']
      if 'dasharray' in cell: dash_bg, dash_fg  = cell['dasharray']
      else:                   dash_bg = dash_fg = 0
      '''
      print(f'{label=} {fill_bg=} {fill_fg=}')
      '''
      row = [
        cell['geom']['name'],
        cell['geom']['size'],
        cell['geom']['facing'],
        fill_fg,
        dash_fg 
      ]
      if fill_bg:                         # z 0
        data[label].append(tuple(['square', 'medium', 'C', fill_bg, dash_bg])) 
      else:
        data[label].append(tuple())
      data[label].append(tuple(row))      # z 1

      if bool(cell['geom']['top']):       # z 2
        data[label].append(tuple(row))

    return data

  def txDbv3Yaml(self, cells, penwidth_mm=Decimal(1)):
    ''' TODO put the loop in block.transforms
    '''
    yaml = dict()
    for label, cell in cells.items():
      #print(label)
      yaml[label] = self.txDbv3YamlOneCell(cell, penwidth_mm)
    #self.pp.pprint(yaml)
    return yaml 

  def txDbv3YamlOneCell(self, cell, penwidth_mm):
    ''' transform V3 to YAML
    '''
    if len(cell[0]): bg = cell[0][3] 
    else           : bg = None
    name, size, facing, fill, dasharray = cell[1]
    dasharray = dasharray if dasharray else 0 # Pydantic wants int
    top = True if len(cell) == 3 else False

    data                        = dict()
    data['geom']                = dict()
    data['color']               = dict()
    data['stroke']              = dict()
    data['geom']['name']        = name
    data['geom']['size']        = size
    data['geom']['facing']      = facing
    data['geom']['top']         = top
    data['color']['background'] = bg
    data['color']['fill']       = fill  # wires crossed in hydrateBlock
    data['color']['opacity']    = 1
    data['stroke']['fill']      = '#000000' # unused except Pydantic
    data['stroke']['opacity']   = 1
    data['stroke']['width']     = f'{penwidth_mm:.2f}'
    data['stroke']['dasharray'] = dasharray
    return data

  def txDbv2Dbv3(self, geom, stk, pal):
    ''' TODO throw this away once db2 is zz
    '''
    dbv3 = dict()
    for label, row in geom.items():
      row2 = list()
      for i, layer in enumerate(row):
        #print(label, i)
        if len(row) == len(pal[label]):
          row2.append(self.txDbv2Dbv3OneCell(layer, pal[label][i], stk[label][i]))
      dbv3[label] = tuple(row2)
    #self.pp.pprint(dbv3)
    return dbv3 

  def txDbv2Dbv3OneCell(self, geom, pal, stk):
    row  = list(geom)
    dash = stk[3]
    dash = None if dash == 0 else dash
    row.append(pal[0])
    row.append(dash)
    return tuple(row)

'''
the
end
'''
