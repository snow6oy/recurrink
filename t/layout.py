import unittest
from svgfile import Layout

class TestLayout(unittest.TestCase):

  def setUp(self):
    self.lt = Layout(scale=1.0)

  def testSize(self):
    ''' size is 54 divided by factor 
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def testScale(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.grid, expected[i])

  def testStyle(self):
    bg, fg = self.lt.style('a', {
      'bg':'#FFF',
      'fill':None,
      'fill_opacity':None,
      'stroke':None,
      'stroke_width':None,
      'stroke_dasharray':None,
      'stroke_opacity':None
    })
    self.assertEqual(bg.get('id'), 'a0')
  # TODO
  def testGridWalk(self):
    cell = {
      'bg': '#DC143C', 'facing': 'east', 'fill': '#4B0082', 'fill_opacity': '1.0',
      'shape': 'line', 'size': 'large', 'stroke': '#DC143C', 'stroke_dasharray': 0,
      'stroke_opacity': '100', 'stroke_width': 6, 'top': False
    }
    top = {
      'bg': '#DC143C', 'facing': 'east', 'fill': '#4B0082', 'fill_opacity': '1.0',
      'shape': 'line', 'size': 'large', 'stroke': '#DC143C', 'stroke_dasharray': 0,
      'stroke_opacity': '100', 'stroke_width': 6, 'top': True
    }
    cells = { 'a': top, 'b': cell, 'c': top, 'd': cell }
    positions = { 
      (0, 0): ('a', 'c'),
      (0, 1): ('c', 'a'),
      (1, 0): 'b',
      (1, 1): 'd',
      (2, 0): ('a', 'c'),
      (2, 1): ('c', 'a')
    }
    lt = Layout(scale=1.0)
    lt.gridwalk((3, 2), positions, cells)
    numof_bg = 0
    for r in list(lt.root.iter(tag=f"{lt.ns}rect")):
      sid, x, y = r.get('id').split('-')
      is_fg = int(sid[1:]) # the last digit of the sid
      numof_bg += 0 if (is_fg) else 1 # count backgrounds to get grid size
    self.assertEqual(numof_bg, (lt.grid * lt.grid))

  def testRenderCell(self):
    pass
  def testRenderBlock(self):
    pass
  '''
  the
  end
  '''


