import unittest
import pprint
from model import Svg
from cell import Geomink
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class Test(unittest.TestCase):

  def setUp(self):
    self.svg    = Svg(scale=1, gridsize=180, cellsize=60)
    self.cell = {
      'bg':'000', 
      'fill': 'FFF',
      'fill_opacity':1, 
      'stroke':'FFF', 
      'stroke_dasharray':0,
      'stroke_opacity':0, 
      'stroke_width':0, 
      'facing': 'north', 
      'size':'medium'
    }
    self.data = config.cells
    self.positions = config.positions

  def test_1(self):
    ''' are diamonds drawn correctly
    '''
    self.cell['shape'] = 'diamond'
    gmk = Geomink(cellsize=60, layer='fg', cell=self.cell, coord=(0, 0))
    self.svg.addStyle('fill:#000', 'a', 1)
    self.svg.addGeomink(1, (0,0), 'a', gmk)
    self.svg.svgDoc(legacy=True)
    self.svg.make()
    el = list(self.svg.root.iter(tag=f"{self.svg.ns}polygon"))[0]
    p = el.get("points").split(',')
    points = list(map(float, p))
    self.assertEqual(points, [0.0, 30.0, 30.0, 0.0, 60.0, 30.0, 0.0, 30.0])

  def test_2(self):
    ''' triangle
    '''
    self.cell['shape'] = 'triangl'
    triangl = Geomink(cellsize=60, layer='fg', cell=self.cell, coord=(0, 0))
    self.svg.addStyle('style', 'a', 1)
    self.svg.addGeomink(1, (0,0), 'a', triangl)
    self.svg.svgDoc(legacy=True)
    self.svg.make()
    self.assertTrue(list(self.svg.root.iter(tag=f"{self.svg.ns}polygon")))

  def test_3(self):
    ''' make a doc for input to Svg()
    '''
    gm = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeCells(blocksz, self.positions, self.data)
    self.svg.styleGuide(block1)
    self.svg.gridWalk(blocksz, block1)
    self.svg.svgDoc(legacy=False)
    #pp.pprint(self.svg.doc)
    self.svg.make()
    self.svg.write('tmp/svgtest_2.svg')
    with open('tmp/svgtest_2.svg') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 37)

  def test_4(self):
    ''' toggle inkscape tags for plotter
    '''
    svg = Svg(scale=1, inkscape=True)
    self.assertTrue(svg.inkscape)
'''
the
end
'''
