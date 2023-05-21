#!/usr/bin/env python3

import os
import inkex
from inkex import Group
import unittest
from recurrink import Draw

BASEDIR = "/home/gavin/code/recurrink"
SVG = None

class Input(inkex.OutputExtension):
  def save(self, stream):
    print('now what')
    stream.write(SVG)

class TestDraw(unittest.TestCase):

  def setUp(self):
    self.d = Draw([
      48,                       # size
      33.25985000000003,        # xOffset
      36.85040500000002         # yOffset
    ])
    self.geometry = {
      'shape':'square',
      'shape_size':'medium',
      'shape_facing':'north',
      'stroke_width': 0
    }

  def test_make_svg(self):
    ''' output to /tmp/test_draw.svg for a visual check
    '''
    svg = inkex.load_svg("samples/test_draw.svg").getroot()
    fg_old = svg.getElementById("fg-old")
    fg_new = self.d.shape('a', 0, 0, self.geometry)
    fg_old.replace_with(fg_new)
    print(fg_old.tostring())
    fg_new.set_id('fg-new')
    #g.add(s)

  def test_triangle(self):
    self.geometry['shape'] = 'triangle'
    s = self.d.shape('a', 0, 0, self.geometry)
    self.assertTrue(s.tag_name == 'polygon')

  def test_diamond(self):
    ''' diamond has a new facing value ALL 
    '''
    self.geometry['shape'] = 'diamond'
    s = self.d.shape('a', 0, 0, self.geometry)
    print(s.get("points"))
    self.assertTrue(s.tag_name == 'polygon')

  def test_bad_facing(self):
    self.geometry['shape_size'] = 'very tiny'
    with self.assertRaises(ValueError):
      self.d.shape('a', 0, 0, self.geometry)

  '''
    the end
  '''
if __name__ == '__main__':
  unittest.main()
