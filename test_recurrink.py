#!/usr/bin/env python3

import os
import unittest
from recurrink import Recurrink

MODLDIR="/home/gavin/Pictures/artWork/recurrences"

class TestRecurrink(unittest.TestCase):

  def setUp(self):
    self.r = Recurrink('soleares')
    self.view = '550d193efe80f67e92d5a0c59ad9d354'

  def test_write_csvfile_machine(self):
    ''' ./recurrink.py -m ${model} --output CSV
    '''
    rr = Recurrink('soleares', machine=True)
    self.assertEqual('a b c d', rr.write_csvfile())

  def test_write_csvfile_human(self):
    self.assertEqual('a b c d', self.r.write_csvfile())
    # os.unlink('/tmp/soleares.csv')

  def test_convert_row2cell(self):
    ''' check vals from csv are correctly poured, e.g. top reordering
        shape: shape_size: shape_facing: fill: bg: fill_opacity: stroke: stroke_width: stroke_dasharray: stroke_opacity: top:
    '''
    d = [[ 'a','soleares','triangle','medium','west','#fff','yellowgreen','1.0','#000','1','0','1.0','False' ],
         [ 'b','soleares','circle','large','all','#fff','yellowgreen','1.0','#000','1','0','1.0','True' ],
         [ 'c','soleares','line','medium','west','#fff','orange','1.0','#000','1','0','1.0','False' ]]
    (model, hashkey, cells) = self.r.convert_row2cell(d)
    sorted_by_top = list(cells.keys())
    self.assertEqual(sorted_by_top, ['a', 'c', 'b'])

  def test_get_cellvalues(self):
    ''' ./recurrink.py -m ${model} --cell ${cell}
    0 1        2      3      4    5    6               7   8    9 0 1   2
    a soleares circle medium west #fff mediumvioletred 1.0 #000 0 0 1.0 True
    '''
    self.r.write_csvfile()
    cells = self.r.get_cellvalues('a').split(' ')
    self.assertTrue(cells[9].isdigit())

  def testWriteView(self):
    new_view = self.r.write_view()
    self.assertEqual(len(new_view), 32)

  def testUpdateView(self):
    ''' when mondrian does updsvg and calls ./recurrink.py -c CELL need to run UPDATE on DB
      this is because mondrian -install no longer copies JSON files aroun
    '''
    view = 'e4681aa9b7aef66efc6290f320b43e55'
    self.assertEqual(view, self.r.write_view(view=view, author='machine'))

  def testWriteRinkfile(self):
    ''' ./recurrink.py -m ${model} --output RINK --view ${view}
        check /tmp/{self.r.model}.rink
    '''
    self.assertEqual(self.r.write_rinkfile('e4681aa9b7aef66efc6290f320b43e55'), '/tmp/soleares.rink')
  ''' the end
  '''
if __name__ == '__main__':
  unittest.main()
