import psycopg2
import pprint
from decimal import *
from config import Db2

class Commit(Db2):

  ''' function to convert celldata to dbrows
  '''
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

        see doc/minkscape_2.py depends on Y3ML
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

'''
the
end
'''
