import unittest
import pprint
from cell import Plotter
from cell import CellMaker
#from cell import Geomink, Plotter
#from block import Flatten
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    #self.f = Flatten()
    self.writer = Plotter()

  def test_1(self):
    ''' poc to see if meander can be called from ShapelyCell
    '''
    expect = [ 
      (1, 1), (1, 5), (2, 5), (2, 1), (3, 1), 
      (3, 5), (4, 5), (4, 1), (5, 1), (5, 5)
    ]
    cm = CellMaker((0, 0), clen=6)
    cm.background('z', {'bg': 'FFF'}) # increment sc.bft
    cm.foreground('z')
    xy = cm.bft[1].this.svg(meander=True)
    self.writer.plotLine(xy, fn='rectangle_1')
    self.assertEqual(expect, list(xy.coords)) 

  def test_2(self):
    ''' north square
    '''
    expect = [ 
      (1,1),(1,8),(2,8),(2,1),(3,1),(3,8),(4,8),(4,1),
      (5,1),(5,8),(6,8),(6,1),(7,1),(7,8),(8,8),(8,1)
    ]
    cm = CellMaker((0,0), clen=9)
    cm.background('z', {'bg': 'FFF'})
    cm.foreground('z')
    xy = cm.bft[1].this.svg(meander=True)
    self.writer.plotLine(xy, fn='rectangle_2')
    self.assertEqual(expect, list(xy.coords))

  def test_3(self):
    ''' east square linefill for Rectangle.meander()

       north ???
      (2,2),(2,6),(3,6),(3,2),(4,2),(4,6),(5,6),(5,2),(6,2),(6,6)
    '''
    expect = [ 
      (1.0, 1.0), (5.0, 1.0), (5.0, 2.0), (1.0, 2.0), (1.0, 3.0), 
      (5.0, 3.0), (5.0, 4.0), (1.0, 4.0), (1.0, 5.0), (5.0, 5.0)
    ]
    cm = CellMaker((0,0), clen=6)
    cm.background('z', {'bg': 'FFF'})
    cm.foreground('z')
    xy = cm.bft[1].this.svg(meander=True, direction='E')
    self.writer.plotLine(xy, fn='rectangle_3')
    self.assertEqual(expect, list(xy.coords)) 
'''
the
end
'''
