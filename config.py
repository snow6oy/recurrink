# minkscape
class config:
  cells = {
    'a': {
      'color': {
        'background': '#F00', 
        'fill': '#090', 
        'opacity': 1.0
      },
      'geom': {
        'name': 'square', 
        'facing': 'C', 
        'size': 'medium', 
        'top': False
      },
      'stroke': {
        'fill': '#090', 
        'dasharray': 0, 
        'opacity': 1, 
        'width': 0.7
      }
    },
    'b': {
      'color': {
        'background': '#F00', 
        'fill': '#00F', 
        'opacity': 1.0
      },
      'geom': {
        'name': 'line', 
        'facing': 'N', 
        'size': 'medium', 
        'top': False
      },
      'stroke': {
        'fill': '#00F', 
        'dasharray': 0, 
        'opacity': 1, 
        'width': 0.7,
      }
    },
    'c': {
      'color': {
        'background': '#F00', 
        'fill': '#00F', 
        'opacity': 1.0
      },
      'geom': {
        'name': 'square', 
        'facing': 'C', 
        'size': 'small', 
        'top': True
      },
      'stroke': {
        'fill': '#00F', 
        'dasharray': 0, 
        'opacity': 1, 
        'width': 0.7
      }
    },
    'd': {
      'color': {
        'background': '#F00', 
        'fill': '#090', 
        'opacity': 1.0
      },
      'geom': {
        'name': 'line', 
        'facing': 'E', 
        'size': 'large', 
        'top': True
      },
      'stroke': {
        'fill': '#090', 
        'dasharray': 0, 
        'opacity': 1, 
        'width': 0.7, 
      }
    }
  }
  positions = {
    (0, 0): ('a', 'c'),  # c is both cell and top
    (1, 0): ('b', 'd'),  # d is only top
    (2, 0): ('c', None)
  }
  friendly_name = [
    None,
    'universal', 
    'colour45', 
    'htmstarter', 
    'jeb', 
    'whitebossa', 
    'snowbg', 
    'solar',
    'uniball',
    'copicsketch',
    'copic',
    'stabilo68',
    'sharpie',
    'staedtler'
  ]
  penam = [{}, {}, {
    '#F00': 'red', '#090': 'green', '#00F': 'blue'
  }]
  directory = {
       'rinks': '/Users/gavin/Dropbox/familia/rinks',
        'pubq': '/Users/gavin/Pictures/pubq',
    'palettes': '/Users/gavin/Library/Application Support/org.inkscape.Inkscape/config/inkscape/palettes'
  }


'''
the
end 
'''
