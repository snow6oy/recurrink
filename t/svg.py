import unittest
import pprint
from model import Svg
from cell import CellMaker
from block import GeoMaker
from config import *
pp = pprint.PrettyPrinter(indent = 2)

class Test(unittest.TestCase):

  def setUp(self):
    self.svg  = Svg(scale=1, gridsize=180, cellsize=60)
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

  # TODO fix transform Layout.addGeomink
  def test_a(self):
    ''' are diamonds drawn correctly
    '''
    self.cell['shape'] = 'diamond'
    #gmk = Geomink(cellsize=60, layer='fg', cell=self.cell, coord=(0, 0))
    cell_a = CellMaker(pos=(0, 0), clen=60)
    cell_a.background('a', self.cell)
    cell_a.foreground('a', self.cell)
    self.svg.addStyle('fill:#000', 'a', 1)
    self.svg.addGeomink(1, (0,0), cell_a.bft[1])
    self.svg.svgDoc()
    self.svg.make()
    el = list(self.svg.root.iter(tag=f"{self.svg.ns}polygon"))[0]
    p = el.get("points").split(',')
    points = list(map(float, p))
    self.assertEqual(points, [0.0, 30.0, 30.0, 0.0, 60.0, 30.0, 0.0, 30.0])

  def test_b(self):
    ''' triangle
    '''
    self.cell['shape'] = 'triangl'
    cell_a = CellMaker(pos=(0, 0), clen=60)
    cell_a.background('a', self.cell)
    cell_a.foreground('a', self.cell)
    self.svg.addStyle('style', 'a', 1)
    self.svg.addGeomink(1, (0,0), cell_a.bft[1])
    self.svg.svgDoc()
    self.svg.make()
    self.assertTrue(list(self.svg.root.iter(tag=f"{self.svg.ns}polygon")))

  def test_c(self):
    ''' make a doc for input to Svg()
    '''
    gm      = GeoMaker()
    blocksz = (3, 1)
    block1  = gm.makeShapelyCells(blocksz, self.positions, self.data)
    self.svg.styleGuide(block1)
    self.svg.gridWalk(blocksz, block1)
    
    self.svg.svgDoc()
    self.svg.make()
    self.svg.write('tmp/t_svg_e.svg')
    with open('tmp/t_svg_e.svg') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 39)

  def test_d(self):
    ''' toggle inkscape tags for plotter
    '''
    svg = Svg(scale=1, inkscape=True)
    self.assertTrue(svg.inkscape)

'''
the
end
'''
