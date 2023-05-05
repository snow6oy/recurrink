#!/usr/bin/env python3


import os
import unittest
from builder import Builder2

MODLDIR="/home/gavin/Pictures/artWork/recurrences"

class TestBuilder2(unittest.TestCase):

  def setUp(self):
    self.b = Builder2('soleares')
    self.view = '550d193efe80f67e92d5a0c59ad9d354'

  def test_load_model(self):
    self.assertEqual(self.b.load_model()[0], ['a', 'b', 'a'])

  def test_bad_model(self):
    with self.assertRaises(KeyError):
      bb = Builder2('fakemodel')  # expect ValueError

  def test_list_model(self):
    self.assertTrue('soleares' in self.b.list_model(MODLDIR))

  def test_write_csvfile_machine(self):
    self.assertEqual('a b c d', self.b.write_csvfile())

  def test_write_csvfile_human(self):
    bb = Builder2('soleares', 'human')
    self.assertEqual('a b c d', bb.write_csvfile())

  def test_write_jsonfile(self):
    ''' human only, machines are random
    '''
    bb = Builder2('soleares', 'human')
    bb.write_csvfile()
    self.assertEqual(self.view, bb.write_jsonfile())

  def test_load_view(self):
    view = self.b.load_view(self.view)
    self.assertEqual(11, len(view['a'].keys()))

  def test_write_rinkfile(self):
    print(self.b.write_rinkfile(self.view))

  ''' the end
  '''
if __name__ == '__main__':
  unittest.main()
