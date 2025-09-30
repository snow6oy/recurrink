import unittest
from cell.shape import Diamond
from cell.minkscape import *
from cell import Layer
from model import SvgWriter

class Test(unittest.TestCase):

  def setUp(self):
    ''' celldata for minkscape 
    '''
    self.VERBOSE = True
    self.cell    = minkscape.cells
    self.clen    = 9 # cell length
    self.layer   = Layer()
    self.writer  = SvgWriter()

  def test_a(self):
    ''' diamond
    '''
    self.cell['d']['geom']['name']   = 'diamond'
    self.cell['d']['geom']['facing'] = 'C'

    points  = self.layer.points(0, 0, 0, self.clen)
    diamond = Diamond()
    polygn  = diamond.coords(points, self.cell['d']['geom'])


    self.assertEqual(diamond.name, 'diamond')
    if self.VERBOSE: self.writer.plot(polygn, self.id()) 
'''
the
end
'''
