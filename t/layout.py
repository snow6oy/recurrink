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
    self.lt = Layout(scale=1.0, gridsize=180)
    self.positions = config.positions
    self.data = config.cells

  def test_1(self):
    expected = [36, 18, 12, 9]
    for i, s in enumerate([0.5, 1.0, 1.5, 2.0]):
      l5 = Layout(scale=s) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
      self.assertEqual(l5.cellnum, expected[i])

  def test_2(self):
    self.lt.uniqstyle(cell='a', layer='bg', top=False, bg='000') 
    self.lt.cells = self.data
    # layer, cell, c, t, gx, x, gy, y
    self.lt.rendercell('bg', 'a', 'a', False, 0, 0, 0, 0) 
    bg = self.lt.doc[0]['shapes'][0]
    self.assertEqual(bg['name'], 'square')

  def test_4(self):
    ''' find style 
    '''
    [self.lt.uniqstyle(
      c, 'bg', self.data[c]['top'], bg='CCC'
    ) for c in self.data]
    #pp.pprint(self.lt.styles)
    style = self.lt.findstyle('a')
    self.assertTrue("fill:#CCC;stroke-width:0", style)

  def test_5(self):
    ''' walk the grid and test if the num of background cells matches gridsize 
    '''
    expected_bg = self.lt.cellnum * self.lt.cellnum
    numof_bg = 0
    self.lt.gridwalk((3, 1), self.positions, self.data)
    #pp.pprint(self.lt.doc[0]['shapes'])
    numof_bg = len(self.lt.doc[0]['shapes'])
    self.assertEqual(numof_bg, expected_bg)

  def test_6(self):
    ''' To plot on A3 should default to 270 when unit is mm
    '''
    lt = Layout(unit='mm')
    gridsize = lt.cellnum * lt.cellsize
    self.assertEqual(gridsize, 270)

  def test_7(self):
    ''' check shape dimensions calculate as expected
    '''
    lt = Layout(scale=1.0, gridsize=18, cellsize=6)
    lt.gridwalk((3, 1), self.positions, self.data)
    #pp.pprint(lt.doc[2])
    self.assertEqual(lt.doc[2]['shapes'][0]['width'], 2)
 
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
    ''' copy bg styles from cells into uniq styles
    '''
    layer = 'bg'
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
    self.assertTrue("fill:#F00;stroke-width:0" in self.lt.styles)

  def test_13(self):
    ''' copy bg from cells into styles and check they arrived ok
    '''
    layer = 'fg'
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
    self.assertTrue("fill:#FF0;fill-opacity:1.0" in self.lt.styles)

  def test_14(self):
    ''' copy from top cells into styles and check they arrived ok
    '''
    layer = 'top'
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
    self.assertTrue("fill:#00F;fill-opacity:1.0" in self.lt.styles)

  def test_15(self):
    ''' style is a dictionary of style:cell names
    '''
    gm = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeCells(blocksz, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.assertEqual(self.lt.lstyles[2]['c'], "fill:#00F;fill-opacity:1.0")

  def test_16(self):
    ''' continue from previous test and then walk the grid
    '''
    gm = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeCells(blocksz, self.positions, self.data)
    self.lt.stampBlocks(blocksz, block1, grid_xy=(0, 0))
    self.assertEqual(list(self.lt.lgmk[0].keys()), ['a','b','c'])

  def test_17(self):
    ''' explode blocks across the grid
    '''
    gm = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeCells(blocksz, self.positions, self.data)
    self.lt.gridWalk(blocksz, block1) # , self.positions, block1)
    self.assertEqual(list(self.lt.lgmk[2].keys())[1], 'd')

  def test_18(self):
    ''' make a doc for input to Svg()
    '''
    gm = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeCells(blocksz, self.positions, self.data)
    self.lt.styleGuide(block1)
    self.lt.gridWalk(blocksz, block1)
    self.lt.svgDoc()
    self.assertEqual(len(self.lt.doc), 5)

'''
the
end
'''
