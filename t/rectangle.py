import unittest
import pprint
from cell import Plotter
from cell import CellMaker
#from cell import Geomink, Plotter
#from block import Flatten
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.writer = Plotter()
    self.VERBOSE = False

  def test_a(self):
    ''' meander called from CellMaker
    '''
    expect = [ 
      (1, 1), (1, 5), (2, 5), (2, 1), (3, 1), 
      (3, 5), (4, 5), (4, 1), (5, 1), (5, 5)
    ]
    cm = CellMaker((0, 0), clen=6)
    cm.background('z', {'bg': 'FFF'}) # increment sc.bft
    cm.foreground('z')
    cm.bft[1].padme()
    xy = cm.bft[1].this.lineFill(facing='all')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_rectangle_a')
    self.assertEqual(expect, list(xy.coords)) 

  def test_b(self):
    ''' north square
    '''
    expect = [ 
      (1,1),(1,8),(2,8),(2,1),(3,1),(3,8),(4,8),(4,1),
      (5,1),(5,8),(6,8),(6,1),(7,1),(7,8),(8,8),(8,1)
    ]
    cm = CellMaker((0,0), clen=9)
    cm.background('z', {'bg': 'FFF'})
    cm.foreground('z')
    cm.bft[1].padme()
    xy = cm.bft[1].this.lineFill(facing='north')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_rectangle_b')
    self.assertEqual(expect, list(xy.coords))

  def test_c(self):
    ''' east square linefill for Rectangle.meander()

    '''
    expect = [ 
      (1.0, 1.0), (5.0, 1.0), (5.0, 2.0), (1.0, 2.0), (1.0, 3.0), 
      (5.0, 3.0), (5.0, 4.0), (1.0, 4.0), (1.0, 5.0), (5.0, 5.0)
    ]
    cm = CellMaker((0,0), clen=6)
    cm.background('z', {'bg': 'FFF'})
    cm.foreground('z')
    cm.bft[1].padme()
    xy = cm.bft[1].this.lineFill(facing='east')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_rectangle_c')
    self.assertEqual(expect, list(xy.coords)) 
'''
the
end
'''
