# minkscape for testing
# also see Y3ML version 3 of YAML in cell/transform.py
class minkscape_2:
  ''' when top is false color len == 2
      otherwise color len == 1
  '''
  cells = {
    'a': {
      'color': ['#F00', '#090'],
      'geom': {
        'name': 'square', 
        'facing': 'C', 
        'size': 'medium', 
        'top': False
      }
    },
    'b': {
      'color': ['#F00', '#00F'],
      'geom': {
        'name': 'line', 
        'facing': 'N', 
        'size': 'medium', 
        'top': False
      }
    },
    'c': {
      'color': ['#F00', '#00F'], 
      'geom': {
        'name': 'square', 
        'facing': 'C', 
        'size': 'small', 
        'top': True
      }
    },
    'd': {
      'color':  [None, '#090'], 
      'dasharray': [None, '3 2 2'], 
      'geom': {
        'name': 'line', 
        'facing': 'E', 
        'size': 'large', 
        'top': True
      }
    }
  }
  positions = {
    (0, 0): ('a', 'c'),  # c is both cell and top
    (1, 0): ('b', 'd'),  # d is only top
    (2, 0): ('c', None)
  }
