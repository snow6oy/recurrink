#!/usr/bin/env python3

'''
export PYTHONPATH=/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions/
this finds inkex.py but then fails due to missing lxml module
lxml is in Inkscape's Python but how to set that context?
'''

import inkex
import unittest

class TestLayoutMethods(unittest.TestCase):

  def setUp(self):
    from draw import Draw
    from configure import Builder, Layout
    model = '03-02d-soleares'
    svg = inkex.load_svg("/home/gavin/Dropbox/geek/SVG/recurrences/soleares.svg").getroot()
    baseUnit = (svg.unittouu(48), svg.unittouu(60), svg.unittouu(64))
    l = Layout(baseUnit)
    l.add(model)
    self.l = l
    d = Draw(baseUnit)
    self.d = d
    self.b = Builder()
  
  def test_scale(self):
    self.assertEqual(self.l.set_scale(0.5), (25.4, 16.0, 8.5))

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
    self.assertEqual(self.d.sizeUu, 12.7)

  def test_triangle(self):
    s = self.d.shape('a', 0, 0, self.l.get_cell('a'))
    self.assertTrue(type(s))

  def test_case_0(self):
    model = '03-02d-soleares'
    self.assertEqual(self.b.load_model(model)[0], ['a', 'b', 'a'])

  def test_case_1(self):
    with self.assertRaises(KeyError):
      self.b.make('fakemodel')  # expect ValueError

if __name__ == '__main__':
  unittest.main()
