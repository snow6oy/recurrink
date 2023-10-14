#!/usr/bin/env python3

''' convert a view into a set of monochrome SVGs for screen printing
'''
import unittest
import pprint
from svgfile import Stencil
pp = pprint.PrettyPrinter(indent=2)

class TestStencil(unittest.TestCase):

  def setUp(self):
    # data source='e4681aa9b7aef66efc6290f320b43e55'
    data = { 
      'a': { 'bg': '#CCC',
         'facing': 'west',
         'fill': '#FFF',
         'fill_opacity': 1.0,
         'shape': 'triangl',
         'size': 'medium',
         'stroke': '#000',
         'stroke_dasharray': 1,
         'stroke_opacity': 0.5,
         'stroke_width': 0,
         'top': False},
      'b': { 'bg': '#CCC',
         'facing': 'all',
         'fill': '#FFF',
         'fill_opacity': 1.0,
         'shape': 'square',
         'size': 'medium',
         'stroke': '#000',
         'stroke_dasharray': 0,
         'stroke_opacity': 1.0,
         'stroke_width': 0,
         'top': False},
      'c': { 'bg': '#CCC',
         'facing': 'all',
         'fill': '#FFF',
         'fill_opacity': 1.0,
         'shape': 'square',
         'size': 'medium',
         'stroke': '#000',
         'stroke_dasharray': 0,
         'stroke_opacity': 1.0,
         'stroke_width': 0,
         'top': False},
      'd': { 'bg': '#32CD32',
         'facing': 'all',
         'fill': '#FFF',
         'fill_opacity': 1.0,
         'shape': 'square',
         'size': 'medium',
         'stroke': '#000',
         'stroke_dasharray': 0,
         'stroke_opacity': '0.5',
         'stroke_width': 0,
         'top': False}}
    self.s = Stencil('soleares', data)
    self.data = data

  def testColourMap(self):
    uniq = self.s.colours()
    [print(colour) for colour in uniq]
    #pp.pprint(self.s.colmap)
    a_bg = self.s.colmap[1]
    self.assertEqual(a_bg, ('a', 'ccc', 'bg'))

  def testCountColour(self):
    uniq = self.s.colours()
    self.assertEqual(len(uniq), 2)
 
  def testMonochrome(self):
    expected = { 'a': '#000', 'b': '#FFF', 'c': '#FFF', 'd': '#FFF' }
    uniq = self.s.colours()
    cccdata = self.s.monochrome('ccc', self.data) # make a stencil for grey only
    #pp.pprint(cccdata)
    [self.assertEqual(expected[c], cccdata[c]['bg']) for c in expected]
  ''' 
  the 
  end
  '''
