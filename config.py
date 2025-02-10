# minkscape
class config:
  cells = {
    'a': {
      'bg': '#F00', 'fill': '#FF0', 'fill_opacity': 1.0,
      'shape': 'square', 'facing': 'all', 'size': 'medium', 'top': False,
      'stroke': '#F00', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    },
    'b': {
      'bg': '#F00', 'fill': '#00F', 'fill_opacity': 1.0,
      'shape': 'line', 'facing': 'north', 'size': 'medium', 'top': False,
      'stroke': '#F00', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    },
    'c': {
      'bg': '#F00', 'fill': '#00F', 'fill_opacity': 1.0,
      'shape': 'square', 'facing': 'all', 'size': 'small', 'top': True,
      'stroke': '#F00', 'stroke_dasharray': 0, 'stroke_opacity': 1.0, 'stroke_width': 0, 
    },
    'd': {
      'bg': '#F00', 'fill': '#FF0', 'fill_opacity': 1.0,
      'shape': 'line', 'facing': 'east', 'size': 'large', 'top': True,
      'stroke': '#F00', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
    }
  }
  positions = {
    (0, 0): ('a', 'c'),  # c is both cell and top
    (1, 0): ('b', 'd'),  # d is only top
    (2, 0): ('c',None)
  }

