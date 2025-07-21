# minkscape
class config:
  cells = {
    'a': {
      'bg': '#F00', 
      'fill': '#090', 
      'fill_opacity': 1.0,
      'shape': 'square', 
      'facing': 'all', 
      'size': 'medium', 
      'top': False,
      'stroke': '#090', 
      'stroke_dasharray': 0, 
      'stroke_opacity': 1, 
      'stroke_width': 0.7, 
    },
    'b': {
      'bg': '#F00', 
      'fill': '#00F', 
      'fill_opacity': 1.0,
      'shape': 'line', 
      'facing': 'north', 
      'size': 'medium', 
      'top': False,
      'stroke': '#00F', 
      'stroke_dasharray': 0, 
      'stroke_opacity': 1, 
      'stroke_width': 0.7, 
    },
    'c': {
      'bg': '#F00', 
      'fill': '#00F', 
      'fill_opacity': 1.0,
      'shape': 'square', 
      'facing': 'all', 
      'size': 'small', 
      'top': True,
      'stroke': '#00F', 
      'stroke_dasharray': 0, 
      'stroke_opacity': 1, 
      'stroke_width': 0.7, 
    },
    'd': {
      'bg': '#F00', 
      'fill': '#090', 
      'fill_opacity': 1.0,
      'shape': 'line', 
      'facing': 'east', 
      'size': 'large', 
      'top': True,
      'stroke': '#090', 
      'stroke_dasharray': 0, 
      'stroke_opacity': 1, 
      'stroke_width': 0.7, 
    }
  }
  positions = {
    (0, 0): ('a', 'c'),  # c is both cell and top
    (1, 0): ('b', 'd'),  # d is only top
    (2, 0): ('c',None)
  }
  friendly_name = [
    'universal', 
    'colour45', 
    'htmstarter', 
    'jeb', 
    'whitebossa', 
    'snowbg', 
    'solar',
    'uniball',
    'copic_sketch',
    'copic',
    'stabilo68'
  ]

'''
the
end 
'''
