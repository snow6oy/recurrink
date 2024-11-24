import unittest
import pprint
from meander import Meander, Plotter
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):
  def setUp(self):
    self.writer  = Plotter()

  def test_1(self): 
    r       = Meander([(3, 3), (3, 15), (15, 15), (15, 3)], direction=(90,405)) 
    padme   = r.pad()
    guides  = r.guidelines(padme)
    self.writer.plot(r.shape, padme, 'meander_1')
    #[print(list(g.coords)) for g in list(guides.geoms)]
    g = list(guides.geoms)[0]
    self.assertEqual(g.coords[0], (4.0, 4.0))

  def test_2(self): 
    ''' Rectangle
    '''
    r       = Meander([(3, 3), (3, 15), (15, 15), (15, 3)], direction=(90,405)) 
    points  = r.collectPoints()
    stripes = r.makeStripes(points)
    self.writer.plotLine(stripes, 'meander_2')

  def test_3(self):
    ''' Gnomon
    '''
    g       = Meander([(3,3), (3,15), (15,15), (15,7), (11,7), (11,3)], direction=(270, 315, 360))
    points  = g.collectPoints()
    stripes = g.makeStripes(points)
    self.writer.plotLine(stripes, 'meander_3')

  def test_4(self):
    ''' two Gnomons make a Polygon with a whole
    '''
    g  = Meander([(3,3),(3,15),(7,15),(7,7),(15,7),(15,3)], direction=(405,45,360))
    p1 = g.collectPoints()
    g  = Meander([(11,7),(11,11),(7,11),(7,15),(15,15),(15,7)], direction=(0,45,90))
    p2 = g.collectPoints()

    stripe = g.joinStripes(p1, p2)
    self.writer.plotLine(stripe, 'meander_4')

  def test_5(self):
    ''' one Gnomon plus Rectangle makes a Parabola
    '''
    g      = Meander([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)], direction=(270,225,180))
    r      = Meander([(0,0),(0,12),(6,12),(6,0)], direction=(360,0))
    p1     = g.collectPoints()
    p2     = r.collectPoints()
    stripe = r.joinStripes(p1, p2)

    self.writer.plotLine(stripe, 'meander_5')

  def test_6(self):
    ''' western Parabola
    '''
    g      = Meander([(0,0),(0,18),(18,18),(18,12),(6,12),(6,0)], direction=(450,135,90))
    r      = Meander([(6,0),(6,6),(18,6),(18,0)], direction=(495,270))
    p1     = g.collectPoints()
    p2     = r.collectPoints()
    stripe = r.joinStripes(p1, p2)
    self.writer.plotLine(stripe, 'meander_6')
    '''
    self.writer.plot(g.shape, r.shape, 'meander_6')
    '''

  def test_7(self):
    ''' eastern Parabola
    '''
    g      = Meander([(0,12),(0,18),(18,18),(18,0),(12,0),(12,12)], direction=(180,225,270))
    r      = Meander([(0,0),(0,6),(12,6),(12,0)], direction=(180,450))     # 495,270))
    p1     = g.collectPoints()
    p2     = r.collectPoints()
    stripe = r.joinStripes(p1, p2)
    self.writer.plotLine(stripe, 'meander_7')
    '''
    self.writer.plot(g.shape, r.shape, 'meander_7')
    padme  = g.pad()
    guides = g.guidelines(padme)
    print(guides)
    '''

'''
the
end
'''
