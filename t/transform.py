import unittest
import pprint
from cell.transform import Transform
from cell.minkscape import *

class Test(unittest.TestCase):

  def setUp(self):
    self.pp    = pprint.PrettyPrinter(indent=2)
    self.tx    = Transform()
    self.cells = minkscape.cells

  def test_a(self, label='a', fg=True, bg=False, top=False, expected=0, i=1):
    #print(f'{fg=} {bg=} {top=} {self.id()}')
    expected = 2 if self.id() == 't.transform.Test.test_a' else expected
    cell = self.tx.dataV2(self.cells['a'])
    cell['shape'] = 'circle'
    cell['top']   = top
    if not bg: cell['bg'] = None
    if top and not fg: cell['top'] = False

    celldata = { label: cell }
    written  = self.tx.dataV1(celldata)
    #self.pp.pprint(written)

    self.assertEqual(len(written[label]), expected) # num of layers
    self.assertEqual('circle', written[label][i][0]) # position of FG or TOP

  def test_b(self): self.test_a(label='b', fg=True, bg=True, expected=2, i=1)
  def test_c(self): 
    self.test_a(label='c', fg=True, bg=True, top=True, expected=3, i=1)
  def test_d(self):
    self.test_a(label='d', fg=False, bg=True, top=True, expected=2, i=1)
  def test_e(self): self.test_a(label='e', fg=True, top=True, expected=3, i=2)

  def test_f(self):
    ''' transform one cell into a flat dictionary
    '''
    cell = self.tx.dataV2(self.cells['b'])
    #self.pp.pprint(cell)
    #print(list(cell.keys()))

    for k in ['shape', 'size', 'facing', 'top', 'bg', 
              'fill', 'fill_opacity', 'stroke', 'stroke_opacity', 
              'stroke_width', 'stroke_dasharray']:
      self.assertTrue(k in cell)

  def test_g(self):
    cell = self.tx.dataV2(self.cells['b'])
    data = self.tx.dataV1({'b': cell})
    #self.pp.pprint(data)
    self.assertEqual(5, len(data['b'][0]))
    self.assertEqual(9, len(data['b'][1]))

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
