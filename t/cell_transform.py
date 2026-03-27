import unittest
import pprint
from cell.transform import Transform
from cell.minkscape import *
from cell.minkscape_2 import *

class Test(unittest.TestCase):

  def setUp(self):
    self.pp    = pprint.PrettyPrinter(indent=2)
    self.tx    = Transform()
    self.cells = minkscape.cells
    self.c3lls = minkscape_2.cells

  def test_a(self, label='a', fg=True, bg=False, top=False, expected=0, i=1):
    #print(f'{label=} {fg=} {bg=} {top=} {self.id()}')
    expected = 2 if self.id() == 't.cell_transform.Test.test_a' else expected
    #cell = self.tx.transformOneCell(self.cells['a'])
    cells                        = self.cells
    cells[label]['geom']['name'] = 'circle'
    cells[label]['geom']['top']  = top
    if not bg: cells[label]['color']['background'] = None
    if top and not fg: cells[label]['geom']['top'] = False
    #self.pp.pprint(cells[label])

    written  = self.tx.dataV2(cells)
    #self.pp.pprint(written[label])
    self.assertEqual(len(written[label]), expected) # num of layers
    self.assertEqual('circle', written[label][i][0]) # position of FG or TOP

  def test_b(self): self.test_a(label='b', fg=True, bg=True, expected=2, i=1)
  def test_c(self): 
    self.test_a(label='c', fg=True, bg=True, top=True, expected=3, i=1)
  def test_d(self):
    self.test_a(label='d', fg=False, bg=True, top=True, expected=2, i=1)
  def test_e(self): self.test_a(label='c', fg=True, top=True, expected=3, i=2)

  def test_f(self):
    ''' transform one cell into a flat dictionary
    '''
    dataV3  = self.tx.dataV3(self.c3lls)
    #self.pp.pprint(dataV3)
    cell    = self.tx.txDbv3YamlOneCell(dataV3['b'])
    #print(list(cell['stroke'].keys()))

    for k in ['name', 'size', 'facing', 'top']:
      self.assertTrue(k in cell['geom'])
    for k in ['background', 'fill', 'opacity']:
      self.assertTrue(k in cell['color'])
    for k in ['fill', 'opacity', 'width', 'dasharray']:
      self.assertTrue(k in cell['stroke'])

  def test_g(self):
    data = self.tx.dataV3(self.c3lls)
    #self.pp.pprint(data)
    self.assertEqual(5, len(data['b'][0]))
    self.assertEqual(0, len(data['d'][0]))

  def test_h(self):
    #self.pp.pprint(self.cells)
    to_write = self.tx.dataV2(self.cells)
    #self.pp.pprint(to_write)
    self.assertEqual(2, len(to_write['a']))
    self.assertEqual(3, len(to_write['c']))
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

cell	z    ver
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
'''
