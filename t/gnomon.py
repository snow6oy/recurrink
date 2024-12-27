import unittest
import pprint
from shapes import Geomink, Plotter
from flatten import Flatten
pp = pprint.PrettyPrinter(indent=2)

  ##########
  # Gnomon #
  ##########

class Test(unittest.TestCase):

  def setUp(self):
    self.f      = Flatten()
    self.done   = Geomink(xywh=(2,2,5,5))
    self.writer = Plotter()

  def test_1(self):
    ''' north west gnomon meander 
    '''
    expect = [(2, 2), (1, 2)]
    seeker = Geomink(xywh=(1,2,5,6))
    self.f.crop(seeker, self.done.shape)
    gnomon = self.f.done[0]
    gmk    = Geomink(polygon=gnomon.shape, label='G1')
    xy     = gmk.meander.fill(direction='NW')
    self.writer.plotLine(xy, fn='gnomon_1')
    self.assertEqual(expect[0], list(xy.coords)[0])
    self.assertEqual(expect[1], list(xy.coords)[-1])
    '''
    self.writer.plot(gnomon.shape, seeker.shape, fn='gnomon_1')
    '''

  def test_2(self):
    ''' south east gnomon meander
    '''
    expect = [(2, 2), (2, 1)]
    seeker = Geomink(xywh=(2,1,6,5))
    self.f.crop(seeker, self.done.shape)
    gnomon = self.f.done[0]
    gmk    = Geomink(polygon=gnomon.shape, label='G1')
    xy     = gmk.meander.fill(direction='SE')
    self.writer.plotLine(xy, fn='gnomon_2')
    self.assertEqual(expect[0], list(xy.coords)[0])
    self.assertEqual(expect[1], list(xy.coords)[-1])
'''
the
end
'''
