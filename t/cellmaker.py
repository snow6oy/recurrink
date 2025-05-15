import unittest
import pprint
from cell.geomink import Plotter
from cell.cellmaker import CellMaker
from shapely.geometry import Polygon
pp = pprint.PrettyPrinter(indent=2)

''' topdown use cases for Minkscape
    tests   CELL.LAYER evalSeeker()
    t1 a1 a0 invisible
    t2 a2 a1 sqring
    t3 b2 b1 multigeom
            hydrate bft before calling flatten
    t4 c1 c0 sqring
    t5 a3 a2 same-as-was
    t6 b2 a2 a1 a0 multi-layered transformation
'''

class Test(unittest.TestCase):

  def setUp(self):
    self.VERBOSE = False
    self.writer  = Plotter()
    clen         = 3
    self.cells   = {
      'a': CellMaker((0, 0), clen), 
      'b': CellMaker((1, 0), clen), 
      'c': CellMaker((2, 0), clen) 
    }

  def test_a(self):
    ''' a1 flattens a0 and makes it Invisible
    '''
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'fill': 'FF0' })
    a0 = self.cells['a'].bft[0]
    a1 = self.cells['a'].bft[1]
    a0 = self.cells['a'].evalSeeker(a1, a0)
    self.assertFalse(a0.this.data) # a1 covers background so it was removed 
    self.assertEqual('Polygon', a1.this.data.geom_type)

  def test_b(self):
    ''' a2 flattens a1 and makes it into a Square Ring
    '''
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'fill': 'FF0' })
    self.cells['a'].top('c', { 'fill': '00F', 'size': 'small' })
    a1 = self.cells['a'].bft[1]
    a2 = self.cells['a'].bft[2]
    a1 = self.cells['a'].evalSeeker(a2, a1)
    self.assertEqual(a1.this.name, 'sqring')
    # plotter cannot render sqring as multigeom ?
    #if self.VERBOSE: self.writer.plot(done.data, seeker.data, fn='cflat_2')

  def test_c(self):
    ''' b2 flattens b1 and returns a MultiPolygon

      [[4, 5, 5, 4, 4], [3, 3, 2, 2, 3]], # N split
      [[4, 5, 5, 4, 4], [1, 1, 0, 0, 1]]  # S split
    '''
    expect = [
      [(5, 3), (5, 2), (4, 2), (4, 3), (5, 3)], # N split
      [(5, 0), (4, 0), (4, 1), (5, 1), (5, 0)]  # S split
    ]
    self.cells['b'].background('b', { 'bg': 'F00' })
    self.cells['b'].foreground('b', { 'shape': 'line' })
    self.cells['b'].top('d', 
      { 'fill': 'FF0', 'shape': 'line', 'facing': 'east', 'size': 'large' }
    )
    b1 = self.cells['b'].bft[1]
    b2 = self.cells['b'].bft[2]
    if self.VERBOSE: self.writer.plot(b2.this.data, b1.this.data, fn='cflat_3')
    b1 = self.cells['b'].evalSeeker(b2, b1)
    self.assertEqual('multipolygon', b1.this.name)
    p1, p2 = b1.this.data.geoms

    self.assertEqual(list(p1.boundary.coords), expect[0])
    self.assertEqual(list(p2.boundary.coords), expect[1])

  def test_d(self):
    ''' c1 flattens c0
        and transform understands a polygon with a hole
    '''
    self.cells['c'].background('c', { 'bg': 'F00' })
    self.cells['c'].foreground('c', { 'fill': 'FF0', 'size': 'small' })
    c0 = self.cells['c'].bft[0]
    c1 = self.cells['c'].bft[1]
    if self.VERBOSE: 
      self.writer.plot(c1.this.data, c0.this.data, fn='t_cellmaker_d')
    self.cells['c'].flatten()
    c0 = self.cells['c'].bft[0]
    self.assertEqual('sqring', c0.this.name)
    c0.tx(4, 4)
    self.assertEqual((13,7), c0.this.data.exterior.coords[0])
    self.assertEqual((13,4), c0.this.data.exterior.coords[1])

  def test_e(self):
    ''' a3 is a dangler from neighbour b2
        it tries to flatten a2 but misses
        a2 is returned unscathed
    '''
    # assume we acquired this dangler from GeoMaker b 2
    dangler = Polygon([(2, 1), (2, 2), (3, 2,), (3, 1), (2, 1)])
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'bg': 'FF0' })
    self.cells['a'].top('c', { 'fill': 'FF0', 'size': 'small' })
    self.cells['a'].void('b', dangler)
    a2 = same = self.cells['a'].bft[2]
    a3 = self.cells['a'].bft[3]
    a2 = self.cells['a'].evalSeeker(a3, a2)
    if self.VERBOSE: self.writer.plot(a3.this.data, a2.this.data, fn='cflat_5')
    self.assertEqual(a2, same)

  def test_f(self):
    ''' b2 flattens a1 then a1 flattens a0
    '''
    # assume we acquired this dangler from GeoMaker b 2
    dangler = Polygon([(2, 1), (2, 2), (3, 2,), (3, 1), (2, 1)])
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'fill': 'FF0' })
    self.cells['a'].top('c', { 'fill': 'FF0', 'size': 'small' })
    self.cells['a'].void('b', dangler)
    self.cells['a'].flatten()
    a3 = self.cells['a'].bft[3] # dangler
    a2 = self.cells['a'].bft[2] # top
    a1 = self.cells['a'].bft[1] # foreground
    a0 = self.cells['a'].bft[0] # background
    if self.VERBOSE: self.writer.plot(a2.this.data, a1.this.data, fn='cflat_6')
    self.assertEqual('void',      a3.this.name)
    self.assertEqual('square',    a2.this.name)
    self.assertEqual('parabola',  a1.this.name)
    self.assertEqual('invisible', a0.this.name)
    #self.assertFalse(seeker)

  def test_g(self):
    ''' check that facing is preserved by compute
    '''
    dangler  = Polygon([(2, 1), (2, 2), (3, 2,), (3, 1), (2, 1)])
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'fill': 'FF0', 'facing': 'west' })
    self.cells['a'].top('c', { 'fill': 'FF0', 'size': 'small' })
    self.cells['a'].void('b', dangler)
    self.cells['a'].flatten()
    self.assertEqual('west', self.cells['a'].bft[1].facing)
    meander = self.cells['a'].bft[1].svg(meander=True)
    # check first two co-ordinates
    self.assertEqual('0.0,0.0,0.0,3.0,3.0,3.0,3.0', meander['points'][:27])

  def test_h(self):
    ''' Shapely.difference() must not create geometries
        with precision less than 1
        otherwise Meander will fail
    '''
    if self.VERBOSE: print(self.id())
    a = CellMaker((0,0), 3)
    a.background('a', {'bg':'FFF'}) 
    a.foreground('a', { 'fill': 'FF0', 'facing': 'all' })
    #Polygon([(2, 1), (2, 2), (3, 2,), (3, 1), (2, 1)]))
    a.bft[1].compute(
      Polygon([(0.0, 0.0), (0.0, 5.3), (3.8, 5.3,), (3.8, 0.0), (0.0, 0.0)])
    )
    b = a.evalSeeker(a.bft[0], a.bft[1])
    '''
      a.bft[0].this.data, a.bft[1].this.data, fn='t_cellmaker_h'
    '''
    if self.VERBOSE: self.writer.plot(
      a.bft[0].this.data, b.this.data, fn='t_cellmaker_h'
    )
    self.assertEqual((0.0, 0.0, 4.0, 5.0), b.this.data.bounds)

  def test_i(self):
    ''' rectangle
    '''
    r     = Polygon([(1, 1), (1, 2), (2, 2), (2, 1)])
    shape = self.cells['a'].shapeTeller(r, 'rectangle')
    self.assertTrue(shape)

  def test_j(self):
    ''' gnomon
    '''
    g = Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 0)])
    shape = self.cells['b'].shapeTeller(g, 'gnomon')
    self.assertTrue(shape)

  def test_k(self):
    ''' parabola
    '''
    p= Polygon([(0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 1), (3, 1), (3, 0)])
    shape = self.cells['c'].shapeTeller(p, 'parabola')
    self.assertTrue(shape)

  def test_l(self):
    ''' square ring
    '''
    hole  = [(1, 1), (1, 2), (2, 2), (2, 1)]
    outer = [(0, 0), (0, 3), (3, 3), (3, 0)]
    sr    = Polygon(outer, holes=[hole])
    shape = self.cells['a'].shapeTeller(sr, 'sqring')
    self.assertTrue(shape)

  def test_m(self):
    ''' dangling extra points
    when shapely operations leave dangling points simplify MIGHT tidy up, e.g.

      clean = polygon.boundary.simplify(tolerance=1)

    but it has unacceptable side-effect of clobbering Gnomons and Parabolas
    this test documents the risk of shapeTeller being fooled by the danglers
  
    Anyway shapeTeller() seems to work
    '''
    r = Polygon([(0, 0), (0, 1), (0, 3), (3, 3), (3, 0)])
    shape = self.cells['a'].shapeTeller(r, 'rectangle')
    self.assertTrue(shape)

  def test_n(self):
    ''' audit flatten by summing up Polygon.area
    '''
    dangler = Polygon([(2, 1), (2, 2), (3, 2,), (3, 1), (2, 1)])
    self.cells['a'].background('a', { 'bg': 'F00' })
    self.cells['a'].foreground('a', { 'fill': 'FF0' })
    self.cells['a'].top('c', { 'fill': 'FF0', 'size': 'small' })
    self.cells['a'].void('b', dangler)
    sum_layered = self.cells['a'].areaSum()
    self.assertEqual((19,8), sum_layered)
    self.cells['a'].flatten()
    sum_flatter = self.cells['a'].areaSum()
    self.assertFalse(sum_flatter[1] - sum_flatter[0])

'''
the
end
'''
