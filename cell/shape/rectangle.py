class Rectangle:

  VERBOSE = False

  def __init__(self, name):
    self.name = name

  def coords(self, x, y, clen, kwargs):
    shape = kwargs['shape']
    size  = kwargs['size']
    facing= kwargs['facing']
    sizes = { 
      'square': {
        'small': [
          x * clen + clen / 3,
          y * clen + clen / 3,
          x * clen + (clen / 3) * 2,
          y * clen + (clen / 3) * 2
        ],
        'medium': [
          x * clen,
          y * clen,
          x * clen + clen,
          y * clen + clen
        ]
      },
      'line': {
        'medium': {
          'north': [
            x * clen + clen / 3,
            y * clen,
            x * clen + (clen / 3) * 2,
            y * clen + clen
          ]
        },
        'large': {
          'east': [  # TODO
            x * clen - clen / 3,
            y * clen + clen / 3,
            x * clen + (clen / 3) * 4,
            y * clen + (clen / 3) * 2
          ]
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
    '''
    control = {
      'N': ('EB', 'ET'),
      'north': ('EB', 'ET'),
      'all': ('EB', 'ET'),
      'S': ('EB', 'ET'),
      'E': ('NL', 'NR'),
      'east': ('NL', 'NR'),
      'W': ('NL', 'NR')
    }
    if direction in control: return control[direction]
    else: # abandon if there are no guidelines defined
      raise KeyError(f'all at sea > {direction=} {self.label=} not found')


