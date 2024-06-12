import unittest
import pprint
from outfile import Layout
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class TestLayout(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape '''
    self.lt = Layout(scale=1.0, gridsize=180)
    self.positions = config.positions
    self.data = config.cells

  def test_0(self):
    ''' size will be divided by scale
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def test_1(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.grid, expected[i])

  def test_2(self):
    self.lt.uniqstyle('a', 'bg', False) 
    self.lt.cells = self.data
    self.lt.rendercell('bg', 'a', 'a', False, 0, 0, 0, 0) # layer, cell, c, t, gx, x, gy, y
    bg = self.lt.doc[0]['shapes'][0]
    self.assertEqual(bg['name'], 'square')

  def test_3(self):
    ''' copy from cells into styles and check they arrived ok
    '''
    for layer in ['bg', 'fg', 'top']:
      for cell in self.data:
        self.lt.uniqstyle(cell, layer, self.data[cell]['top'],
          bg=self.data[cell]['bg'],
          fill=self.data[cell]['fill'],
          fo=self.data[cell]['fill_opacity'],
          stroke=self.data[cell]['stroke'],
          sd=self.data[cell]['stroke_dasharray'],
          so=self.data[cell]['stroke_opacity'],
          sw=self.data[cell]['stroke_width']
        )
      if layer == 'bg':
        self.assertTrue("fill:#CCC;stroke-width:0" in self.lt.styles)
        self.assertEqual(self.lt.styles["fill:#CCC;stroke-width:0"], [ 'a', 'b', 'c', 'd' ])
      elif layer ==  'fg' and self.data[cell]['stroke_width']:
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
      elif layer == 'top' and self.data[cell]['stroke_width']:
        self.assertEqual(
          self.lt.styles[
            "fill:#FFF;fill-opacity:1.0;stroke:#000;stroke-width:0;stroke-dasharray:0;stroke-opacity:0"
          ], [ 'd' ]
        )
      elif layer == 'top':
        self.assertTrue("fill:#FFF;fill-opacity:1.0" in self.lt.styles)
      self.lt.styles.clear()

  def test_4(self):
    ''' find style '''
    [self.lt.uniqstyle(c, 'bg', self.data[c]['top']) for c in self.data]
    #pp.pprint(self.lt.styles)
    style = self.lt.findstyle('a')
    self.assertTrue("fill:#CCC;stroke-width:0", style)

  def test_5(self):
    ''' walk the grid and test if the number of background cells matches gridsize 
    '''
    expected_bg = self.lt.grid * self.lt.grid
    numof_bg = 0
    self.lt.gridwalk((3, 1), self.positions, self.data)
    #pp.pprint(self.lt.doc[0]['shapes'])
    numof_bg = len(self.lt.doc[0]['shapes'])
    self.assertEqual(numof_bg, expected_bg)

  def test_6(self):
    ''' A4 is 210mm wide: test for excessive page widths
    '''
    lt = Layout(scale=2.0, gridsize=360, cellsize=24)
    self.assertFalse(lt.A4_OK)
    lt = Layout(scale=2.0, gridsize=180, cellsize=24)
    self.assertTrue(lt.A4_OK)

  def test_7(self):
    ''' check shape dimensions calculate as expected
    '''
    lt = Layout(scale=1.0, gridsize=18, cellsize=6)
    lt.gridwalk((3, 1), self.positions, self.data)
    # pp.pprint(lt.doc[2])
    self.assertEqual(lt.doc[2]['shapes'][0]['width'], 2)
 
  def test_8(self):
    ''' is the given scale within range
    '''
    self.assertRaises(ValueError, Layout, scale=2.9, gridsize=1080, cellsize=60) # scale 2.9
    self.assertRaises(ValueError, Layout, scale=2.9, gridsize=180, cellsize=24)  # is not valid

  def test_9(self):
    ''' cell size must be divisble by 3 for cubes
    '''
    self.assertRaises(ValueError, Layout, cellsize=2)
'''
the
end
'''

