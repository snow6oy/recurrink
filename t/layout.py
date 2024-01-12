import unittest
import pprint
from svgfile import Layout
pp = pprint.PrettyPrinter(indent = 2)

class TestLayout(unittest.TestCase):

  def setUp(self):
    self.lt = Layout(scale=1.0, gridpx=180)
    self.positions = { 
      (0, 0): ('a', 'c'),  # c is both cell and top
      (1, 0): ('b', 'd'),  # d is only top
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
        'shape': 'square', 'facing': 'all', 'size': 'small', 'top': True,
        'stroke': '#000', 'stroke_dasharray': 3, 'stroke_opacity': 1.0, 'stroke_width': 9, 
      },
      'd': {
        'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
        'shape': 'line', 'facing': 'east', 'size': 'large', 'top': True,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      }
    }

  def testSize(self):
    ''' size will be divided by scale
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def testScale(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.grid, expected[i])

  def test_3(self):
    ''' copy from cells into styles and check they arrived ok
    '''
    for layer in ['bg', 'fg', 'top']:
      for cell in self.cells:
        self.lt.uniqstyle(cell, layer, self.cells[cell]['top'],
          bg=self.cells[cell]['bg'],
          fill=self.cells[cell]['fill'],
          fo=self.cells[cell]['fill_opacity'],
          stroke=self.cells[cell]['stroke'],
          sd=self.cells[cell]['stroke_dasharray'],
          so=self.cells[cell]['stroke_opacity'],
          sw=self.cells[cell]['stroke_width']
        )
      if layer == 'bg':
        self.assertTrue("fill:#CCC;stroke-width:0" in self.lt.styles)
        self.assertEqual(self.lt.styles["fill:#CCC;stroke-width:0"], [ 'a', 'b', 'c', 'd' ])
      elif layer ==  'fg' and self.cells[cell]['stroke_width']:
        self.assertTrue(
          "fill:#FFF;fill-opacity:1.0;stroke:#000;stroke-width:0;stroke-dasharray:0;stroke-opacity:0" in self.lt.styles
        )
        self.assertEqual(
          self.lt.styles[
            "fill:#FFF;fill-opacity:1.0;stroke:#000;stroke-width:0;stroke-dasharray:0;stroke-opacity:0"
          ], [ 'a', 'd' ]
        )
      elif layer ==  'fg':
        self.assertTrue("fill:#FFF;fill-opacity:1.0" in self.lt.styles)
      #  "fill:#000;fill-opacity:1.0;stroke:#000;stroke-width:0;stroke-dasharray:0;stroke-opacity:0": [ 'b', 'c' ]
      elif layer == 'top' and self.cells[cell]['stroke_width']:
        self.assertEqual(
          self.lt.styles[
            "fill:#FFF;fill-opacity:1.0;stroke:#000;stroke-width:0;stroke-dasharray:0;stroke-opacity:0"
          ], [ 'd' ]
        )
      elif layer == 'top':
        self.assertTrue("fill:#FFF;fill-opacity:1.0" in self.lt.styles)
      self.lt.styles.clear()

  def testFindStyle(self):
    [self.lt.uniqstyle(c, 'bg', self.cells[c]['top']) for c in self.cells]
    #pp.pprint(self.lt.styles)
    style = self.lt.findstyle('a')
    self.assertTrue("fill:#CCC;stroke-width:0", style)

  def testGridWalk(self):
    self.lt.gridwalk((3, 1), self.positions, self.cells)
    self.lt.write('/tmp/minkscape.svg')
    numof_bg = 0
    for g in list(self.lt.root.iter(tag=f"{self.lt.ns}g")):
      gid = g.get('id')
      if int(gid) == 1:
        numof_bg = len(list(g.iter())[1:]) # the first item is g so ignore it
    self.assertEqual(numof_bg, (self.lt.grid * self.lt.grid))

  # TODO
  def testRenderCell(self):
    self.lt.uniqstyle('a', 'bg', False) 
    self.lt.rendercell('bg', 'a', 'a', False, 0, 0, 0, 0) # layer, cell, c, t, gx, x, gy, y
    bg = self.lt.root[1][0]
    self.assertEqual(bg.get('id'), '2')

  '''
  the
  end
  '''
