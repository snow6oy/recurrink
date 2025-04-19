import unittest
import pprint
# from cell.geomink import Geomink, Plotter
from cell.shape import ShapelyCell
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def test_1(self):
    ''' does shapely return the expected boundary for our rectangle
    '''
    expect = ([[2, 2, 4, 4, 2], [2, 4, 4, 2, 2]])

    sc  = ShapelyCell(pos=(1, 1), clen=2)
    box = sc.box((4, 4))
    xy  = list(box.this.data.boundary.xy)
    '''
    gmk = Geomink(cellsize=15, xywh=(2, 2, 4, 4))
    xy = list(gmk.shape.boundary.xy)
    print(list(gmk.shape.boundary.xy))
    '''
    self.assertEqual(xy[0].tolist(), expect[0])
    self.assertEqual(xy[1].tolist(), expect[1])

  def test_2(self):
    ''' create geomink from cell db 
    '''
    c   = {
      'bg':'000', 'fill_opacity':1, 'stroke':'FFF', 'stroke_dasharray':0,
      'stroke_opacity':0, 'stroke_width':100, 'facing': 'all', 'size':'medium'
    }
    sc  = ShapelyCell(pos=(0, 0), clen=15) # fake cell length
    sc.background('R', c)
    bg = sc.bft[0]
    #gmk = Geomink(cellsize=15, layer='bg', cell=c, coord=(2, 2))
    #self.assertTrue(gmk.shape.bounds, (2.0, 2.0, 17.0, 17.0))
    self.assertEqual(bg.this.data.bounds, (0, 0, 15, 15))

  def test_3(self):
    ''' geomink has attributes to create Layout.uniqStyle() 
    '''
    cell = config.cells['a']
    sc  = ShapelyCell(pos=(2, 2), clen=15)
    sc.background('a', cell)
    gmk = sc.bft[0]
    self.assertEqual(gmk.label, 'a')
    self.assertEqual(gmk.this.data.bounds, (30, 30, 45, 45))
    self.assertEqual(gmk.fill, 'F00')
    '''
    self.assertFalse(gmk.stroke['width'])
    gmk = Geomink(cellsize=15, layer='bg', cell=cell, coord=(2, 2)) 
    self.assertEqual(gmk.label, 'R')
    self.assertEqual(gmk.shape.bounds, (30, 30, 45, 45))
    self.assertEqual(gmk.layer, 'bg')
    self.assertEqual(gmk.fill, 'F00')
    self.assertFalse(gmk.stroke['width'])
    '''
'''
the
end
'''
