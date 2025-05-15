import unittest
import pprint
from shapely.geometry import Polygon
from cell import CellMaker, Plotter

############
# Parabola #
############

class Test(unittest.TestCase):
  def setUp(self):
    self.VERBOSE = False
    self.writer = Plotter()

  def test_a(self):
    ''' southern parabola CCW=False

      (5,15),(5,5),(15,5),(15,6),(6,6),(6,15),(7,15),(7,7),
      (15,7),(15,9),(15,15),(14,15),(14,9),(13,9),(13,15)
    '''
    expect = [ 
      (1,11),(1,1),(11,1),(11,2),(2,2),(2,11),(3,11),(3,3),
      (11,3),(11,5),(11,11),(10,11),(10,5),(9,5),(9,11)
    ]
    a = CellMaker((0,0), clen=12)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(4,4), (4,12), (8,12), (8,4), (4,4)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    #a.bft[0].padme()
    #a.bft[1].padme()
    xy = a.bft[0].this.lineFill(facing='south')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_a')
    self.assertEqual(expect, list(xy.coords))
    '''
    if self.VERBOSE: self.writer.plot(a.bft[0].this.data,b, fn='t_parabola_a')
    '''

  def test_b(self):
    ''' southern parabola CCW=True
    '''
    expect = [ 
      (14,1),(1,1),(1,14),(2,14),(2,2),(14,2),(14,3),
      (3,3),(3,14),(4,14),(4,4),(14,4),(14,6),(14,14),
      (13,14),(13,6),(12,6),(12,14),(11,14),(11,6)
    ]
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,5), (5,15), (10,15), (10,5), (5,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='south')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_b')
    self.assertEqual(expect, list(xy.coords))

  def test_c(self):
    ''' eastern meander with CCW False
    '''
    expect = [ 
      (1,17),(17,17),(17,1),(16,1),(16,16),(1,16),(1,15),(15,15),
      (15,1),(14,1),(14,14),(1,14),(1,13),(13,13),(13,1),(11,1),
      (1,1),(1,2),(11,2),(11,3),(1,3),(1,4),(11,4),(11,5),(1,5)
    ]
    a = CellMaker((0,0), clen=18)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(0,6), (0,12), (12,12), (12,6), (0,6)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='east')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_c')
    self.assertEqual(expect, list(xy.coords))

  def test_d(self):
    ''' eastern meander with CCW True
    '''
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(0,5), (0,10), (10,10), (10,5), (0,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='east')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_d')
    self.assertEqual((14,1), list(xy.coords)[0])
    self.assertEqual((9,4), list(xy.coords)[-1])

  def test_e(self):
    ''' west meander CCW = False
    '''
    a = CellMaker((0,0), clen=18)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(6,6), (18,6), (18,12), (6,12), (6,6)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='west')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_e')
    self.assertEqual((17,17), list(xy.coords)[0])
    self.assertEqual((17,5),  list(xy.coords)[-1])

  def test_f(self):
    ''' west parabola meander CCW = True
    '''
    expect = [
      (1,1),(1,14),(14,14),(14,13),(2,13),(2,1),(3,1),
      (3,12),(14,12),(14,11),(4,11),(4,1),(6,1),(6,4),
      (7,4),(7,1),(8,1),(8,4),(9,4),(9,1),(10,1),(10,4),
      (11,4),(11,1),(12,1),(12,4),(13,4),(13,1),(14,1),(14,4)
    ]
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,5), (5,10), (15,10), (15,5), (5,5)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='west')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_f')
    self.assertEqual(expect, list(xy.coords))

  def test_g(self):
    ''' north meander CCW False
    '''
    expect = [
      (1,1),(1,11),(11,11),(11,10),(2,10),(2,1),(3,1),(3,9),
      (11,9 ),(11,7 ),(11,1),(10,1),(10,7 ),(9 ,7 ),(9 ,1)
    ]
    a = CellMaker((0,0), clen=12)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(4,0), (4,8), (8,8), (8,0), (4,0)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='north')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_g')
    self.assertEqual(expect, list(xy.coords))

  def test_h(self):
    ''' north meander CCW True
    '''
    a = CellMaker((0,0), clen=15)
    a.background('a', {'bg':'FFF'})
    b = Polygon([(5,0), (5,10), (10,10), (10,0), (5,0)])
    a.void('b', b) # pass in a dangler
    a.flatten()    # convert background
    self.assertEqual('parabola', a.bft[0].this.name)
    xy = a.bft[0].this.svg(meander=True, facing='north')
    if self.VERBOSE: self.writer.plotLine(xy, fn='t_parabola_h')
    self.assertEqual((14,14), list(xy.coords)[0])
    self.assertEqual((11,1), list(xy.coords)[-1])

'''
the
end
'''
