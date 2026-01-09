import unittest
import pprint
from block import Db2

# TODO merge with t.geometry
class Test(unittest.TestCase):
  ''' tests depend on this entry 
      run after mid:1 and ver:1 have been created

INSERT INTO rinks (rinkid, mid, ver)
VALUES ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',1,1);
  '''

  def setUp(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    self.db2    = Db2()
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
    self.cell = {
                'bg': None,
             'shape': 'circle',
              'size': 'medium',
            'facing': 'C',
               'top': False,
              'fill': '#ccff00',
      'fill_opacity': 1.0,
            'stroke': '#ff00cc',
    'stroke_opacity': 0.5,
      'stroke_width': 1,
  'stroke_dasharray': 2
    }

  def test_a(self, label='a', fg=True, bg=False, top=False, expected=2):
    #print(f'{fg=} {bg=} {top=} {self.id()}')
    cell = self.cell
    cell['top'] = top
    if bg: cell['bg'] = '#00cc00',
    if top and not fg: cell['top'] = False # demote to layer 1

    celldata     = { label: cell }
    nrc, written = self.db2.geometryWrite(self.rinkid, celldata)
    self.assertEqual(expected, nrc) # check rows were inserted

  def test_b(self): self.test_a(label='b', fg=True, bg=True, expected=2)
  def test_c(self): 
    self.test_a(label='c', fg=True, bg=True, top=True, expected=3)
  def test_d(self):
    self.test_a(label='d', fg=False, bg=True, top=True, expected=2)
  def test_e(self): self.test_a(label='e', fg=True, top=True, expected=3)

  def test_f(self):
    ''' read test cell from geometry table
    '''
    expected = {
      'a': 2, 'b': 2, 'c': 3, 'd': 2, 'e': 3
    } 
    cells    = self.db2.geometryRead(self.rinkid)
    #self.pp.pprint(cells)
    for label in ['a', 'b', 'c', 'd', 'e']:
      self.assertEqual(expected[label], len(cells[label]))
    
  def test_g(self):
    ''' test the transformer
    '''
    cell = self.cell
    #self.pp.pprint(cell)
    cell = self.db2.dataV1({'a': cell})
    self.assertFalse(len(cell['a'][0]))
    self.assertTrue(len(cell['a'][1]))

  def test_h(self, label='h', bg=None):
    ver          = 1
    cell         = self.cell
    cell['bg']   = bg if bg else None
    celldata     = { label: cell }
    nrc, written = self.db2.paletteWrite(self.rinkid, ver, celldata)
    #print(f'{nrc=}')
    #self.pp.pprint(written)
    self.assertEqual(2, nrc)

  def test_i(self): self.test_h(label='i', bg='#000000')

  def test_j(self):
    pal = self.db2.paletteRead(self.rinkid)
    self.assertTrue(pal)

  def test_k(self, label='k', width=1, top=False):
    ''' write strokes
    '''
    ver          = 1
    cell         = self.cell
    cell['stroke_width'] = width
    cell['top']  = top
    
    celldata     = { label: cell }
    nrc, written = self.db2.strokeWrite(self.rinkid, ver, celldata)
    self.assertTrue(nrc >= 2)
    # print(f'{nrc=}')
    # self.pp.pprint(written)

  def test_l(self): self.test_k(label='l', width=0)
  def test_m(self): self.test_k(label='m', top=True)

  def test_n(self):
    ''' read strokes
    '''
    expected = { 'k': 2, 'l': 2, 'm': 3 }
    s        = self.db2.strokeRead(self.rinkid)
    [self.assertEqual(expected[label], len(s[label])) for label in ['k', 'l', 'm']] 
    #self.pp.pprint(s)

  def test_z(self):
    print( """
Now remember to clean up after the test

DELETE FROM geometry WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
DELETE FROM palette  WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
DELETE FROM strokes  WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
""")


'''
CELL    FG	BG	TOP	BG
a       y   n	  n	  n
b	      y   y	  n	  n
c       y   y	  y	  n
d       n   n	  y	  y
e	      y	  n	  y	  n

TOP has two versions of truth
it is definetly True when a cell position
has both FG and TOP allocated

cells that are marked as TOP but 
are uniquely allocated to a position without a FG (e.g. cell d)
are also TOP.
These should be allocated a BG as if they were a FG
And demoted to layer 1

cell	z    BGs
--------------------
a     0    n
a     1    y
b     0    y
b	    1    y
c	    0    y
c	    1    y
c	    2    y
d	    0    y
d	    1    y
e     0    n
e	    1    y
e	    2    y

the 
end
'''
