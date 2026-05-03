import psycopg2
import pprint
from decimal import *
from config import Db2

class Clone(Db2):

  ''' function to convert dbrows to celldata
  '''
  def databaseToYaml(self, cell, penwidth_mm=Decimal(1)):
    ''' transform V3 to YAML
    '''
    if len(cell) == 1: print('trubble ahead')
    if len(cell[0]): bg = cell[0][3] 
    else           : bg = None
    # TODO cells with null backgrounds are sent with fg only :/
    name, size, facing, fill, dasharray = cell[1]
    '''
    else:  
      name, size, facing, fill, dasharray = 'square', 'medium', 'C', bg, 0
    '''
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

'''
the
end
'''
