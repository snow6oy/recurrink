import pprint
import random
#import psycopg2
#from config import *
#from .shape import *

class Init:

  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self, colors):
    self.colors = colors

  def generate(self, top, axis=None, facing_c=False, facing=None, stroke=None):
    #print(f"{axis=} {top=} {facing_c=} {facing=} {stroke=}")
    geometry = Geometry()
    palette  = Palette()
    strokes  = Strokes()

    if axis:
      g = geometry.generateOne(axis, top, facing)
    else:
      if facing_c: g = geometry.generateFacingCentre(top)
      else:        g = geometry.generateFacingAny(top)
    p = palette.generateOne(self.colors)
    s = strokes.generateOne(self.colors)

    '''
    data = g | p | s
    self.pp.pprint(data)
    '''
    data           = dict()
    data['geom']   = g
    data['color']  = p
    if s: data['stroke'] = s
    #else: data['stroke'] = None

    return data 
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Geometry():
  ''' Generate a geometry by random selecting class properties
      to validate input geometries see block.validate
  '''

  def __init__(self):
    self.shape = [
      'circle', 'line', 'square', 'triangl', 'diamond', 'gnomon', 'parabol'
    ]
    self.attributes = {
      'circle': { 
        'size'  : ['small', 'medium', 'large'], 'facing': ['C']
      },
      'line': { 
        'size'  : ['small', 'medium', 'large'], 'facing': ['N', 'S', 'E', 'W']
      },
      'square': { 
        'size'  : ['small', 'medium', 'large'], 'facing': ['C']
      },
      'triangl': { 
        'size'  : ['medium'], 'facing': ['N', 'S', 'E', 'W']
      },
      'diamond': { 
        'size'  : ['medium'], 'facing': ['C', 'N', 'S', 'E', 'W']
      },
      'gnomon': { 
        'size'  : ['medium', 'small'], 'facing': ['NE', 'SE', 'NW', 'SW']
      },
      'parabol': { 
        'size'  : ['medium'], 'facing': ['N', 'S', 'E', 'W']
      },
    }
    self.flip = {
       'E': { 'N': 'S', 'S': 'N' },
       'N': { 'W': 'E', 'E': 'W' },
      'NE': { 'N': 'E', 'E': 'N' },
      'SW': { 'S': 'W', 'W': 'S' }
    }
    self.defaults = { 
      'name':'square', 'size':'medium', 'facing':None, 'top':False 
    }

  def generateFacingAny(self, top=False):
    s    = random.choice(self.shape)
    z    = random.choice(self.attributes[s]['size'])
    f    = random.choice(self.attributes[s]['facing'])
    data = dict(zip(['name','size','facing','top'], [s, z, f, top]))
    return data

  def generateFacingCentre(self, top=False):
    geom = random.choice(self.candidates(['C']))
    geom.append(top)
    data = dict(zip(['name','size','facing','top'], geom))
    return data

  def generateOne(self, axis, top, facing=None):
    ''' use the compass and pair cells along the axis
    '''
    flip    = self.flip[axis]
    geom    = random.choice(self.candidates(list(flip.keys())))
    geom[2] = flip[facing] if facing else geom[2] 
    geom.append(top)
    data    = dict(zip(['name','size','facing','top'], geom))
    return data

  def candidates(self, facing):
    ''' filter by facing
        NOTE makes western line and IT IS FINE
    '''
    candidates = list()
    for f in facing:
      for shape in self.attributes:
        if f not in self.attributes[shape]['facing']: continue
        size = random.choice(self.attributes[shape]['size'])
        candidates.append([shape, size, f])
        #print(f'{f=} {shape=} {size=}')
    return candidates

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Palette():

  def __init__(self):
    self.zeroten = [n for n in range(1, 11)]

  def generateOne(self, colors):
    fill = random.choice(colors)
    bg   = random.choice(colors)
    op   = random.choice(self.zeroten) / 10
    return dict(zip(['fill','background','opacity'], [fill[0], bg[0], op]))

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Strokes(Palette):

  ''' stroke dasharray is a space separated pair LEN GAP
      e.g. when width=5 dasharray:5 5 makes cubes
  '''
  def __init__(self):
    self.zeroten = [n for n in range(1, 11)]

  def generateOne(self, colors):
    ''' generate one stroke from color set
    '''
    YN     = random.choice([True, False]) # fifty fifty chance to get a stroke
    color  = random.choice(colors)
    stroke = color[0]
    width  = random.choice(self.zeroten)
    dash   = 1 if YN else 0
    op     = random.choice(self.zeroten) / 10
    '''
    empty  = { 
           'fill': None,
          'width': None, 
      'dasharray': None,
        'opacity': None 
    }
    '''
    return dict(
      zip(['fill','width','dasharray','opacity'], 
      [stroke, width, dash, op])
    ) if YN else None

'''
the
end
'''
