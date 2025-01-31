import unittest
import pprint
from cell import Geomink, Plotter
from block import Flatten
pp = pprint.PrettyPrinter(indent=2)

  ##########
  # Gnomon #
  ##########

class Test(unittest.TestCase):

  def setUp(self):
    self.f      = Flatten()
    self.done   = Geomink(cellsize=9, xywh=(2,2,5,5))
    self.writer = Plotter()

  def test_1(self):
    ''' north west gnomon meander 
    '''
    expect = [(2, 2), (1, 2)]
    seeker = Geomink(cellsize=9, xywh=(1,2,5,6))
    self.f.crop(seeker, self.done.shape)
    gmk = self.f.get('G1')
    xy  = gmk.meander.fill(direction='NW')
    self.writer.plotLine(xy, fn='gnomon_1')
    self.assertEqual(expect[0], list(xy.coords)[0])
    self.assertEqual(expect[1], list(xy.coords)[-1])
    self.writer.plot(gmk.shape, seeker.shape, fn='gnomon_1')

  def test_2(self):
    ''' south east gnomon meander
    '''
    expect = [(2, 2), (2, 1)]
    seeker = Geomink(cellsize=9, xywh=(2,1,6,5))
    self.f.crop(seeker, self.done.shape)
    gmk    = self.f.get('G1')
    xy     = gmk.meander.fill(direction='SE')
    self.writer.plotLine(xy, fn='gnomon_2')
    self.assertEqual(expect[0], list(xy.coords)[0])
    self.assertEqual(expect[1], list(xy.coords)[-1])
'''
the
end
'''
