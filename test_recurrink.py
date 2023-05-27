#!/usr/bin/env python3


import os
import unittest
from recurrink import Builder

MODLDIR="/home/gavin/Pictures/artWork/recurrences"

class TestBuilder(unittest.TestCase):

  def setUp(self):
    self.b = Builder('soleares')
    self.view = '550d193efe80f67e92d5a0c59ad9d354'

  def test_load_model(self):
    self.assertEqual(self.b.load_model()[0], ['a', 'b', 'a'])

  def test_bad_view(self):
    with self.assertRaises(FileNotFoundError):
      self.b.find_recurrence(self.view, 'XXX')

  def test_list_model(self):
    self.assertTrue('soleares' in self.b.list_model())

  def test_write_csvfile_machine(self):
    ''' ./recurrink.py -m ${model} --output CSV
    '''
    bb = Builder('soleares', machine=True)
    self.assertEqual('a b c d', bb.write_csvfile())

  def test_write_csvfile_human(self):
    self.assertEqual('a b c d', self.b.write_csvfile())
    os.unlink('/tmp/soleares.csv')

  def test_convert_row2cell(self):
    ''' check vals from csv are correctly poured, e.g. top reordering
        shape: shape_size: shape_facing: fill: bg: fill_opacity: stroke: stroke_width: stroke_dasharray: stroke_opacity: top:
    '''
    d = [[ 'a','soleares','triangle','medium','west','#fff','yellowgreen','1.0','#000','1','0','1.0','False' ],
         [ 'b','soleares','circle','large','all','#fff','yellowgreen','1.0','#000','1','0','1.0','True' ],
         [ 'c','soleares','line','medium','west','#fff','orange','1.0','#000','1','0','1.0','False' ]]
    (model, hashkey, cells) = self.b.convert_row2cell(d)
    sorted_by_top = list(cells.keys())
    self.assertEqual(sorted_by_top, ['a', 'c', 'b'])

  def test_get_cellvalues(self):
    ''' ./recurrink.py -m ${model} --cell ${cell}
    0 1        2      3      4    5    6               7   8    9 0 1   2
    a soleares circle medium west #fff mediumvioletred 1.0 #000 0 0 1.0 True
    '''
    self.b.write_csvfile()
    cells = self.b.get_cellvalues('a').split(' ')
    self.assertTrue(cells[9].isdigit())

  def test_write_jsonfile(self):
    ''' ./recurrink.py -m ${model} --output JSON --random
    '''
    bb = Builder('soleares', machine=True)
    bb.write_csvfile()  # generate random CSV
    self.assertTrue(self.b.write_jsonfile())

  def test_write_jsonfile_human(self):
    ''' ./recurrink.py -m ${model} --output JSON
    '''
    self.b.write_csvfile()
    self.assertEqual(self.view, self.b.write_jsonfile())

  def test_load_view(self):
    ''' assume that b.find_recurrence was used to populate jsonfile
    '''
    json_file = f'soleares/h/{self.view}.json'
    view = self.b.load_view(json_file)
    self.assertEqual(11, len(view['a'].keys()))

  def test_write_rinkfile(self):
    ''' ./recurrink.py -m ${model} --output RINK
        check /tmp/{self.b.model}.rink
    '''
    self.assertFalse(self.b.write_rinkfile())
  ''' the end

  '''
if __name__ == '__main__':
  unittest.main()
