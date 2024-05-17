#!/usr/bin/env python3

''' convert a view into a set of monochrome SVGs for screen printing
'''
import unittest
import pprint
from outfile import Stencil
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

  def test_0(self):
    ''' Count Colour 
    '''
    uniq = self.s.colours()
    self.assertEqual(len(uniq), 2)
 
  def test_1(self):
    ''' Colour Map
    '''
    uniq = self.s.colours()
    #[print(colour) for colour in uniq]
    pp.pprint(self.s.colmap)
    a_bg = self.s.colmap[1]
    self.assertEqual(a_bg, ('a', 'ccc', 'bg'))

  def test_2(self):
    ''' Monochrome
    '''
    expected = { 'a': '#000', 'b': '#FFF', 'c': '#FFF', 'd': '#FFF' }
    uniq = self.s.colours()
    cccdata = self.s.monochrome('ccc', self.data) # make a stencil for grey only
    #pp.pprint(cccdata)
    [self.assertEqual(expected[c], cccdata[c]['bg']) for c in expected]

  def test_3(self):
    ''' Buleria data is different 
    '''
    data = { 
      'a': { 'bg': '#00F',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': None,
         'stroke_dasharray': None,
         'stroke_opacity': None,
         'stroke_width': 0,
         'top': False},
      'b': { 'bg': '#F00',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': '#000',
         'stroke_dasharray': 0,
         'stroke_opacity': '1.0',
         'stroke_width': 2,
         'top': False},
      'c': { 'bg': '#FFF',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': None,
         'stroke_dasharray': None,
         'stroke_opacity': None,
         'stroke_width': 0,
         'top': False},
      'd': { 'bg': '#00F',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': None,
         'stroke_dasharray': None,
         'stroke_opacity': None,
         'stroke_width': 0,
         'top': False},
      'e': { 'bg': '#000',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': None,
         'stroke_dasharray': None,
         'stroke_opacity': None,
         'stroke_width': 0,
         'top': False},
      'f': { 'bg': '#FF0',
         'facing': 'all',
         'fill': '#F00',
         'fill_opacity': '1.0',
         'shape': 'square',
         'size': 'small',
         'stroke': None,
         'stroke_dasharray': None,
         'stroke_opacity': None,
         'stroke_width': 0,
         'top': False}}
    s = Stencil('buleria', data, gcode=True)
    uniqcol = s.colours()
    #pp.pprint(s.colmap)
    #pp.pprint(uniqcol)
    [self.assertTrue(f in uniqcol) for f in ['fill:#000', 'fill:#00F', 'fill:#F00', 'fill:#FF0', 'fill:#FFF']]

  ''' 
  the 
  end
  '''
