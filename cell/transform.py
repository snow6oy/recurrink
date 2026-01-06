import psycopg2
import pprint

class Transform:

  ''' generic functions to convert celldata to cellrows and back again
      celldata is flat as returned by db1
  '''
  def dataV1(self, celldata):
    ''' create layered data structure
        BG and FG are mandatory TOP is optional
        see t.geometry for use cases
    '''
    data = dict()
    for label, cell in celldata.items():
      if label not in data: data[label] = list()
      bg  = cell['bg']
      row = [
        cell['shape'],
        cell['size'],
        cell['facing'],
        cell['fill'],
        cell['fill_opacity']
      ]
      if cell['stroke_width'] > 0:
        row += [
          cell['stroke'],
          cell['stroke_opacity'],
          cell['stroke_width'],
          cell['stroke_dasharray']
         ]

      if bg:
        data[label].append(tuple(['square', 'medium', 'C', bg, 1])) # z 0
      else:
        data[label].append(tuple())

      data[label].append(tuple(row)) # z 1

      if bool(cell['top']): # z 2
        data[label].append(tuple(row))

    return data

  def dataV2(self, cell):
    ''' convert nested dict into V1 dict 
        and then return layered object
    '''
    data                 = dict()
    data['shape']        = cell['geom']['name']
    data['size']         = cell['geom']['size']
    data['facing']       = cell['geom']['facing']
    data['top']          = cell['geom']['top']
    data['bg']           = cell['color']['background']
    data['fill']         = cell['color']['fill']
    data['fill_opacity'] = cell['color']['opacity']

    if 'stroke' in cell:
      data['stroke']           = cell['stroke']['fill']
      data['stroke_opacity']   = cell['stroke']['opacity']
      data['stroke_width']     = cell['stroke']['width']
      data['stroke_dasharray'] = cell['stroke']['dasharray']
    return data
