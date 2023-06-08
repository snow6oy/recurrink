#!/usr/bin/env python3

import os
import json
import inkex
import unittest
from layout import Layout
# have a few setup dependencies on Builder
from recurrink import Recurrink

BASEDIR="/home/gavin/code/recurrink"

class TestLayout(unittest.TestCase):

  def setUp(self):
    r = Recurrink('soleares')
    rinkdata = r.load_rinkdata('e4681aa9b7aef66efc6290f320b43e55')
    l = Layout()
    l.add('soleares', rinkdata)
    self.l = l
  
  def test_scale(self):
    l5 = Layout(factor=0.5)
    self.assertEqual((l5.size, l5.width, l5.height), (96.0, 1122.5197, 793.70081))

  def test_cell_a(self):
    self.assertFalse(self.l.get_cell('a')['top'])

  def test_uniq_cells(self):
    self.assertEqual(self.l.uniq_cells(), ['a','b','c','d'])

  def test_blocksize(self):
    self.assertEqual(self.l.blocksize(), (3,2))
  '''
  def test_get_id(self):
    self.assertEqual(self.l.get_id(), 'soleares')
  '''
  def test_positions(self):
    rs = []
    for y in range(2):
      for x in range(3):
        #print(f"y={y} x={x}")
        rs.append(self.l.get_cell_by_position(x, y))
    self.assertEqual(rs, ['a','b','a','c','d','c'])

  def test_sizeUu(self):
    self.assertEqual(self.l.sizeUu, 48.0)

  def test_top(self):
    ''' test_card.rink uses top but will Layout reorder correctly
    '''
    #print(os.getcwd())
    with open(f'{BASEDIR}/samples/test_card.json') as f:
      testdb = json.load(f)
    rink = self.l.add('soleares', testdb)
    self.assertTrue(rink['cells']['b']['top'])
    self.assertFalse(rink['cells']['c']['top'])

  '''
    the end
  '''
if __name__ == '__main__':
  unittest.main()
