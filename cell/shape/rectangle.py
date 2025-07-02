class Rectangle:

  VERBOSE = False

  def __init__(self, name):
    self.name = name

  def coords(self, dim, kwargs):
    ''' calculate bounding coords for a Shapely polygon
    '''
    X, Y, W, H, a, b, c, d, A, B, C, D = dim

    shape = kwargs['shape']
    size  = kwargs['size']
    facing= kwargs['facing']
    sizes = { 
      'square': {
        'small': [a, b, c, d],
       'medium': [X, Y, W, H],
        'large': [A, B, C, D]
      },
      'line': {
        'medium': {
          'north': [a, Y, c, H],
          'south': [a, Y, c, H],
           'east': [X, b, W, d],
           'west': [X, b, W, d]
        },
        'small': {  # TODO same as small square so deprecate in the interface
          'north': [a, b, c, d],
          'south': [a, b, c, d],
           'east': [a, b, c, d],
           'west': [a, b, c, d]
        },
        'large': {
         'north': [a, B, c, D],
         'south': [a, B, c, D],
          'west': [A, b, C, d],
          'east': [A, b, C, d]
        }
      }
    }
    if shape in sizes and size in sizes[shape]:
      if shape == 'square':
        x, y, w, h = sizes[shape][size]
      elif facing in sizes[shape][size]:
        x, y, w, h = sizes[shape][size][facing]
      else:
        raise NotImplementedError(f'{shape=} {size=} {facing=}')
    else: 
      raise NotImplementedError(f'{shape=} {size=}')

    if self.VERBOSE: print(f'{shape=} {size=} {facing=} {x} {y} {w} {h}')
    return ((x, y), (x, h), (w, h), (w, y))

  def guide(self, direction):
    ''' expand facing to a pair of guidelines for meander

        TODO are the NSEW aliases used?
    '''
    control = {
        'all': ('spiral'),  # TODO EB ET
          'N': ('EB', 'ET'),
      'north': ('EB', 'ET'),
          'S': ('EB', 'ET'),
      'south': ('EB', 'ET'),
          'E': ('NL', 'NR'),
       'east': ('NL', 'NR'),
          'W': ('NL', 'NR'),
       'west': ('NL', 'NR'),
    }
    if direction in control: return control[direction]
    else: # abandon if there are no guidelines defined
      raise KeyError(f'all at sea > {direction=} {self.name=} not found')

'''
the
end
'''
