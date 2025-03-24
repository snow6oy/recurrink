import unittest
import pprint
from model import Layout
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.lt        = Layout(scale=1.0, gridsize=180)
    self.gm        = GeoMaker()
    self.positions = config.positions
    self.data      = config.cells
    self.blocksize = (3, 1)

  def test_1(self):
    ''' check shape dimensions calculate as expected
        NOTE this test fails unless runs first ???
    '''
    lt     = Layout(scale=1.0, gridsize=18, cellsize=6)
    gm     = GeoMaker(cellsize=6)
    block1 = gm.makeCells(self.blocksize, self.positions, self.data)
    lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    x, y, w, h = lt.lgmk[1]['b'][0].shape.bounds
    self.assertEqual(int(w - x), 2)

  def test_2(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.cellnum, expected[i])

  def test_3(self):
    ''' background cells have to be square
    '''
    block1  = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    bg = [x.name for cn in ['a','b','c'] for x in self.lt.lgmk[0][cn]]
    self.assertEqual(len(set(bg)), 1)

  def test_4(self):
    ''' style is a dictionary of style:cell names
    '''
    block1  = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.assertEqual(self.lt.lstyles[2]['c'], "fill:#00F;fill-opacity:1.0")

  def test_5(self):
    ''' find style 
    '''
    self.lt.addStyle('fill:#CCC;stroke-width:0', 'a', 0)
    style = self.lt.lstyles[0]['a']
    self.assertTrue('fill:#CCC;stroke-width:0', style)

  def test_7(self):
    ''' walk the grid and test if the num of background cells matches gridsize 
    '''
    numof_bg    = 0
    expected_bg = self.lt.cellnum * self.lt.cellnum
    block1      = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.gridWalk(self.blocksize, block1)
    for cn in ['a', 'b', 'c']:
      numof_bg += len(self.lt.lgmk[0][cn])
    self.assertEqual(numof_bg, expected_bg)

  def test_6(self):
    ''' To plot on A3 should default to 270 when unit is mm
    '''
    lt = Layout(unit='mm')
    gridsize = lt.cellnum * lt.cellsize
    self.assertEqual(gridsize, 270)

  def test_8(self):
    ''' is the given scale within range
    '''
    # scale 2.9
    self.assertRaises(ValueError, Layout, scale=2.9, gridsize=1080, cellsize=60)
    # is not valid
    self.assertRaises(ValueError, Layout, scale=0.6, gridsize=180, cellsize=24)

  def test_9(self):
    ''' cell size must be divisble by 3 for cubes
    '''
    self.assertRaises(ValueError, Layout, cellsize=2)

  def test_10(self):
    ''' only mm and px allowed
    '''
    self.assertRaises(ValueError, Layout, unit='zz')

  def test_11(self):
    ''' size will be divided by scale
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def test_12(self):
    ''' continue from previous test and then walk the grid
    '''
    block1  = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    self.assertEqual(list(self.lt.lgmk[0].keys()), ['a','b','c'])

  def test_13(self):
    ''' explode blocks across the grid
    '''
    block1  = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.gridWalk(self.blocksize, block1)
    self.assertEqual(list(self.lt.lgmk[2].keys())[1], 'd')

  def test_14(self):
    ''' make a doc for input to Svg()
    '''
    block1  = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc()
    self.assertEqual(len(self.lt.doc), 5)

  def test_15(self):
    '''
    check circles are supported by makeCells
    { 'cx': 75.0, 'cy': 15.0, 'name': 'circle', 'r': 21}
    '''
    has_circle = False
    self.data['c']['shape'] = 'circle'  # force it for testing
    block1 = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc(legacy=True)
    for group in self.lt.doc:
      for shape in group['shapes']:
        if shape['name'] == 'circle'and 'cx' in shape:
          has_circle = True
          break
    self.assertTrue(has_circle)

  def test_16(self):
    ''' triangles
    { 'name': 'triangl',
      'points': '990.0,1065.0,1020.0,1050.0,1020.0,1080.0,990.0,1065.0'},
    '''
    has_triangl = False
    self.data['b']['shape'] = 'triangl'  # force it for testing
    block1 = self.gm.makeCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc(legacy=True)
    for group in self.lt.doc:
      for shape in group['shapes']:
        if shape['name'] == 'triangl'and 'points' in shape:
          has_triangl = True
          break
    self.assertTrue(has_triangl)
'''
the
end
'''
