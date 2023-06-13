#!/usr/bin/env python3

import os.path
import unittest
from recurrink import Recurrink
#, Cells, Blocks, Models

class TestRecurrink(unittest.TestCase):

  def setUp(self):
    self.r = Recurrink('soleares')
    self.view = '550d193efe80f67e92d5a0c59ad9d354'

  def test_write_csvfile_machine(self):
    ''' ./recurrink.py -m ${model} --output CSV
    '''
    self.assertEqual('a b c d', self.r.init(rnd=True))

  def test_write_csvfile_human(self):
    self.assertEqual('a b c d', self.r.init())

  def testTopOk2Commit(self):
    ''' check vals from csv are correctly poured, e.g. top reordering
        shape shape_size shape_facing top fill bg fill_opacity stroke stroke_width stroke_dasharray stroke_opacity 
    '''
    d = [[ 'a','soleares','triangle','medium','west','#fff','yellowgreen','1.0','#000','1','0','1.0','False' ],
         [ 'b','soleares','circle','large','all','#fff','yellowgreen','1.0','#000','1','0','1.0','True' ],
         [ 'c','soleares','line','medium','west','#fff','orange','1.0','#000','1','0','1.0','False' ]]
    cells = self.r.commit(d)
    sorted_by_top = list(cells.keys())
    self.assertEqual(sorted_by_top, ['a', 'c', 'b'])

  def testGetCellValues(self):
    ''' ./recurrink.py -m ${model} --cell ${cell}
    0 1        2      3      4    5    6               7   8    9 0 1   2
    a soleares circle medium west #fff mediumvioletred 1.0 #000 0 0 1.0 True
    '''
    if os.path.isfile('/tmp/soleares.csv'):
      cells = self.r.update('soleares')
      #pp.pprint(cells['a'])
      self.assertFalse(cells[9].isdigit())
    else:
      pass
  ''' the end
  '''

