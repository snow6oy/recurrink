import unittest
from svgfile import Layout

class TestLayout(unittest.TestCase):

  def setUp(self):
    self.lt = Layout(scale=1.0, gridpx=180)
    self.positions = { 
      (0, 0): ('a', None),
      (1, 0): ('b', 'd'),
      (2, 0): ('c',None)
    }
    self.cells = {
      'a': {
        'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
        'shape': 'circle', 'facing': 'all', 'size': 'medium', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      },
      'b': {
        'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
        'shape': 'line', 'facing': 'north', 'size': 'medium', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      },
      'c': {
        'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
        'shape': 'square', 'facing': 'all', 'size': 'small', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      },
      'd': {
        'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
        'shape': 'line', 'facing': 'east', 'size': 'large', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      }
    }

  def testSize(self):
    ''' size is 54 divided by factor 
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def testScale(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.grid, expected[i])

  def testUniqStyle(self):
    [self.lt.uniqstyle(cell, 'bg', bg='#CCC') for cell in self.cells]
    self.assertEqual(len(self.lt.groups), 4)

  def testGridWalk(self):
    self.lt.gridwalk((3, 1), self.positions, self.cells)
    numof_bg = 0
    for r in list(self.lt.root.iter(tag=f"{self.lt.ns}rect")):
      sid, x, y = r.get('id').split('-')
      is_fg = int(sid[1:]) # the last digit of the sid
      numof_bg += 0 if (is_fg) else 1 # count backgrounds to get grid size
    self.assertEqual(numof_bg, (self.lt.grid * self.lt.grid))

  # TODO
  def testRenderCell(self):
    pass
  '''
  the
  end
  '''
