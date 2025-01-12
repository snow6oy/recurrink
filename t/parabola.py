import unittest
import pprint
from shapely.geometry import Polygon
from flatten import Flatten
from shapes import Geomink, Plotter
pp = pprint.PrettyPrinter(indent=2)

############
# Parabola #
############

class Test(unittest.TestCase):
  def setUp(self):
    self.f = Flatten()
    self.writer = Plotter()

  def test_1(self):
    ''' southern parabola CCW=False
    '''
    expect = [ 
      (5,15),(5,5),(15,5),(15,6),(6,6),(6,15),(7,15),(7,7),
      (15,7),(15,9),(15,15),(14,15),(14,9),(13,9),(13,15)
    ]
    done   = Geomink(xywh=(8,8,12,16))
    seeker = Geomink(xywh=(4,4,16,16))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='S')
    self.writer.plotLine(xy, fn='parabola_1')
    self.assertEqual(expect, list(xy.coords))

  def test_2(self):
    ''' southern parabola CCW=True
    '''
    expect = [ 
      (15,2),(2,2),(2,15),(3,15),(3,3),(15,3),(15,4),(4,4),(4,15),(5,15),(5,5),
      (15,5),(15,7),(15,15),(14,15),(14,7),(13,7),(13,15),(12,15),(12,7)
    ]
    done   = Geomink(xywh=(6,6,11,16))
    seeker = Geomink(xywh=(1,1,16,16))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='S')
    self.writer.plotLine(xy, fn='parabola_2')
    self.assertEqual(expect, list(xy.coords))

  def test_3(self):
    ''' eastern meander with CCW False
    '''
    expect = [ 
      (1,17),(17,17),(17,1),(16,1),(16,16),(1,16),(1,15),(15,15),
      (15,1),(14,1),(14,14),(1,14),(1,13),(13,13),(13,1),(11,1),
      (1,1),(1,2),(11,2),(11,3),(1,3),(1,4),(11,4),(11,5),(1,5)
    ]
    done   = Geomink(xywh=(0,6,12,12))
    seeker = Geomink(xywh=(0,0,18,18))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='E')
    self.writer.plotLine(xy, fn='parabola_3')
    self.assertEqual(expect, list(xy.coords))
    
  def test_4(self):
    ''' eastern meander with CCW True
    '''
    done   = Geomink(xywh=(1,6,11,11))
    seeker = Geomink(xywh=(1,1,16,16))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='E')
    self.writer.plotLine(xy, fn='parabola_4')
    self.assertEqual((15,2), list(xy.coords)[0])
    self.assertEqual((10,5), list(xy.coords)[-1])

  def test_5(self):
    ''' west meander CCW = False
    '''
    done   = Geomink(xywh=(7,7,19,13))
    seeker = Geomink(xywh=(1,1,19,19))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='W')
    self.writer.plotLine(xy, fn='parabola_5')
    self.assertEqual(list(xy.coords)[0],  (18,18))
    self.assertEqual(list(xy.coords)[-1], (18, 6))

  def test_6(self):
    ''' west parabola meander CCW = True
    '''
    expect = [
      (1,1),(1,14),(14,14),(14,13),(2,13),(2,1),(3,1),(3,12),(14,12),(14,11),(4,11),(4,1),
      (6,1),(6,4),(7,4),(7,1),(8,1),(8,4),(9,4),(9,1),(10,1),(10,4),(11,4),(11,1),(12,1),
      (12,4),(13,4),(13,1),(14,1),(14,4)
    ]
    done   = Geomink(xywh=(5,5,15,10))
    seeker = Geomink(xywh=(0,0,15,15))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='W')
    self.writer.plotLine(xy, fn='parabola_6')
    self.assertEqual(expect, list(xy.coords))

  def test_7(self):
    ''' north meander CCW False
    '''
    expect = [
      (5,5),(5,15),(15,15),(15,14),(6,14),(6,5),(7,5),(7,13),
      (15,13),(15,11),(15,5),(14,5),(14,11),(13,11),(13,5)
    ]
    done   = Geomink(xywh=(8,4,12,12))
    seeker = Geomink(xywh=(4,4,16,16))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='N')
    self.writer.plotLine(xy, fn='parabola_7')
    self.assertEqual(expect, list(xy.coords))

  def test_8(self):
    ''' north meander CCW True
    '''
    done   = Geomink(xywh=(6,1,11,11))
    seeker = Geomink(xywh=(1,1,16,16))
    self.f.crop(seeker, done.shape)
    gmk = self.f.get('P1')
    xy = gmk.meander.fill(direction='N')
    self.writer.plotLine(xy, fn='parabola_8')
    self.assertEqual((15,15), list(xy.coords)[0])
    self.assertEqual((12,2), list(xy.coords)[-1])

  def test_9(self):
    ''' can shapeTeller tell if I am a parabola that can be meandered
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    self.assertTrue(self.f.shapeTeller(p, 'parabola'))

  def test_10(self):
    ''' same test as above but with identify
    '''
    p = Polygon([(0,0), (0,9), (9,9), (9,0), (6,0), (6,3), (3,3), (3,0)])
    self.assertEqual('P', self.f.identify(p))

  def test_11(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    self.assertFalse(self.f.shapeTeller(p, 'parabola'))

  def test_12(self):
    ''' only divisible by three parabolas are irregular 
    '''
    p = Polygon([(0,0), (0,8), (8,8), (9,0), (6,0), (6,2), (2,2), (2,0)])
    self.assertEqual('I', self.f.identify(p))

'''
the
end
'''
