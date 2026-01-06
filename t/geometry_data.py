import unittest
import pprint
from block import Db2

# TODO merge with t.geometry
class Test(unittest.TestCase):
  ''' tests depend on this entry 
      needs to run after mid:1 and ver:1 have been created

INSERT INTO rinks (rinkid, mid, ver)
VALUES ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',1,1);
  '''

  def setUp(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    self.db2    = Db2()
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'

  def test_a(self, label='a', fg=True, bg=False, top=False, expected=0, i=0):
    # print(f'{fg=} {bg=} {top=} {self.id()}')
    expected = 1 if self.id() == 't.geometry_write.Test.test_a' else expected
    cell = {
          'bg': None,
       'shape': 'circle',
        'size': 'medium',
      'facing': 'C',
         'top': top
    }
    if bg: cell['bg'] = '#00cc00',
    if top and not fg: cell['top'] = False

    celldata     = { label: cell }
    nrc, written = self.db2.geometryWrite(self.rinkid, celldata)
    #self.pp.pprint(written)

    self.assertEqual(1, nrc) # check rows were inserted
    self.assertEqual(len(written[label]), expected) # num of layers
    self.assertEqual('circle', written[label][i][0]) # position of FG or TOP

  def test_b(self): self.test_a(label='b', fg=True, bg=True, expected=2, i=1)
  def test_c(self): 
    self.test_a(label='c', fg=True, bg=True, top=True, expected=3, i=1)
  def test_d(self):
    self.test_a(label='d', fg=False, bg=True, top=True, expected=2, i=1)
  def test_e(self): self.test_a(label='e', fg=True, top=True, expected=2, i=0)

  def test_f(self):
    ''' read test cell from geometry table
    '''
    expected = {
      'a': 1, 'b': 2, 'c': 3, 'd': 2, 'e': 2
    } 
    cells    = self.db2.geometryRead(self.rinkid)
    for label in ['a', 'b', 'c', 'd', 'e']:
      self.assertEqual(expected[label], len(cells[label]))
    

  def test_z(self):
    print( """
Now remember, after each run need to manually clean

DELETE FROM geometry WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
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

cell	z
---------
a 0
b 0
b	1
c	0
c	1
c	2
d	0
d	1
e	0
e	1

'''
'''

