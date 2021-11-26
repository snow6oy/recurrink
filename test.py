#!/usr/bin/env python3

'''
export PYTHONPATH=/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions/
this finds inkex.py but then fails due to missing lxml module
lxml is in Inkscape's Python but how to set that context?
'''

import inkex
import unittest
from configure import Builder, Layout
from draw import Draw

class TestLayoutMethods(unittest.TestCase):

  def setUp(self):
    model = 'soleares'
    svg = inkex.load_svg("/home/gavin/Dropbox/geek/SVG/recurrences/soleares.svg").getroot()
    l = Layout()
    l.add(model)
    d = Draw([l.size, l.width, l.height])
    self.d = d
    self.l = l
    self.b = Builder()
  
  def test_scale(self):
    l5 = Layout(factor=0.5)
    self.assertEqual((l5.size, l5.width, l5.height), (96.0, 1122.5197, 793.70081))

  def test_cell_a(self):
    self.assertFalse(self.l.get_cell('a')['top'])

  def test_uniq_cells(self):
    self.assertEqual(self.l.uniq_cells(), ['a','b','c','d'])

  def test_blocksize(self):
    self.assertEqual(self.l.blocksize(), (3,2))

  def test_get_id(self):
    self.assertEqual(self.l.get_id(), '8b2c78bf119f3082714dabb23d5d46dc')

  def test_positions(self):
    rs = []
    for y in range(2):
      for x in range(3):
        #print(f"y={y} x={x}")
        rs.append(self.l.get_cell_by_position(x, y))
    self.assertEqual(rs, ['a','b','a','c','d','c'])

  def test_sizeUu(self):
    self.assertEqual(self.d.sizeUu, 48.0)

  def test_triangle(self):
    s = self.d.shape('a', 0, 0, self.l.get_cell('a'))
    self.assertTrue(type(s))

  def test_case_0(self):
    model = 'soleares'
    self.assertEqual(self.b.load_model(model)[0], ['a', 'b', 'a'])

  def test_case_1(self):
    with self.assertRaises(KeyError):
      self.b.make('fakemodel')  # expect ValueError
  '''
  '''
if __name__ == '__main__':
  unittest.main()
