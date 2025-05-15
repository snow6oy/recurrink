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

  def test_a(self):
    ''' check shape dimensions calculate as expected
        NOTE this test fails unless runs first ???
    '''
    lt     = Layout(scale=1.0, gridsize=18, cellsize=6)
    gm     = GeoMaker(cellsize=6)
    block1 = gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    x, y, w, h = lt.lgmk[1]['b'][0].this.data.bounds
    self.assertEqual(int(w - x), 2)

  def test_b(self):
    ''' background cells have to be square
    '''
    lt     = Layout(scale=1.0, gridsize=180)
    gm     = GeoMaker()
    block1 = gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    lt.styleGuide(block1)
    lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    labels = [x.label for cn in ['a','b','c'] for x in lt.lgmk[0][cn]]
    self.assertEqual(['a','b','c'], labels)

  def test_c(self):
    ''' walk the grid and test if the num of background cells matches gridsize 
    '''
    lt          = Layout(scale=1.0, gridsize=180)
    numof_bg    = 0
    expected_bg = self.lt.cellnum * self.lt.cellnum
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    lt.gridWalk(self.blocksize, block1)
    for cn in ['a', 'b', 'c']:
      numof_bg += len(lt.lgmk[0][cn])
    self.assertEqual(numof_bg, expected_bg)

  def test_d(self):
    ''' style is a dictionary of style:cell names
    '''
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    style_part = self.lt.lstyles[2]['c'][:26]
    self.assertEqual('fill:#00F;fill-opacity:1.0', style_part)

  def test_e(self):
    ''' find style 
    '''
    self.lt.addStyle('fill:#CCC;stroke-width:0', 'a', 0)
    style = self.lt.lstyles[0]['a']
    self.assertTrue('fill:#CCC;stroke-width:0', style)

  def test_f(self):
    ''' To plot on A3 should default to 270 when unit is mm
    '''
    lt = Layout(unit='mm')
    gridsize = lt.cellnum * lt.cellsize
    self.assertEqual(gridsize, 270)

  def test_g(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.cellnum, expected[i])

  def test_h(self):
    ''' is the given scale within range
    '''
    # scale 2.9
    self.assertRaises(ValueError, Layout, scale=2.9, gridsize=1080, cellsize=60)
    # is not valid
    self.assertRaises(ValueError, Layout, scale=0.6, gridsize=180, cellsize=24)

  def test_i(self):
    ''' cell size must be divisble by 3 for cubes
    '''
    self.assertRaises(ValueError, Layout, cellsize=2)

  def test_j(self):
    ''' only mm and px allowed
    '''
    self.assertRaises(ValueError, Layout, unit='zz')

  def test_k(self):
    ''' size will be divided by scale
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def test_l(self):
    ''' continue from previous test and then walk the grid
    '''
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.stampBlocks(self.blocksize, block1, grid_xy=(0, 0))
    self.assertEqual(list(self.lt.lgmk[0].keys()), ['a','b','c'])

  def test_m(self):
    ''' explode blocks across the grid
    '''
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.gridWalk(self.blocksize, block1)
    self.assertEqual(list(self.lt.lgmk[2].keys())[1], 'd')

  def test_n(self):
    ''' make a doc for input to Svg()
    '''
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc()
    self.assertEqual(6, len(self.lt.doc))

  def test_o(self):
    '''
    check circles are supported by geomaker
    { 'cx': 75.0, 'cy': 15.0, 'name': 'circle', 'r': 21}
    '''
    has_circle = False
    self.data['c']['shape'] = 'circle'  # force it for testing
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc()
    for group in self.lt.doc:
      for shape in group['shapes']:
        if shape['name'] == 'circle'and 'cx' in shape:
          has_circle = True
          break
    self.assertTrue(has_circle)

  def test_p(self):
    ''' triangles
    { 'name': 'triangl',
      'points': '990.0,1065.0,1020.0,1050.0,1020.0,1080.0,990.0,1065.0'},
    '''
    has_triangl = False
    self.data['b']['shape'] = 'triangl'  # force it for testing
    block1 = self.gm.makeShapelyCells(self.blocksize, self.positions, self.data)
    self.lt.styleGuide(block1)
    ''' 
    fails here as Shapely.transform says Triangles are MultiPoint
    '''
    self.lt.gridWalk(self.blocksize, block1)
    self.lt.svgDoc()
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
