#!/usr/bin/env python3
import os.path
import unittest
import pprint
from cell import Palette
from config import *

class Test(unittest.TestCase):
  ''' opaque palettes are valid because non-square shapes display background
      all fg/bg combinations are also valid even when fg and bg are the same
  '''

  def setUp(self):
    self.p  = Palette(ver=1)  # colour45 is default
    self.pp = pprint.PrettyPrinter(indent=2)
    self.defaults = {
      'color': {
        'fill': '#FFF',
        'background': '#CCC',
        'opacity':1.0,
      }
    }

  def test_a(self):
    fnam = self.p.friendlyPenNames()
    self.assertEqual('htmstarter', fnam[3])

  def test_b(self):
    ''' validate bad fill fails
    '''
    self.p.loadPalette()
    data = self.defaults
    data['fill'] = '#zzzzzz' 
    self.assertRaises(ValueError, self.p.validate, 'a', data)

  def test_c(self):
    ''' Load Palette
    '''
    p = Palette(ver=3)
    p.loadPalette(ver=3)
    self.assertTrue(len(p.palette), 25)
    self.assertEqual(p.opacity, [1.0])
    self.assertEqual(p.complimentary['#FFF'], '#FFF')

  def test_d(self):
    ''' Generate One randomly generate first cell of pair 
        and then allocate complimentary to the second cell 
    '''
    self.p.loadPalette(ver=1)
    pairs = ('b', 'd')       # compass.one(axis) for context
    cell_b = self.p.generate_one(ver=1)
    cell_d = self.p.generate_one(ver=1, primary=cell_b)
    #self.pp.pprint(cell_d)
    test = cell_b['fill']
    self.assertEqual(self.p.complimentary[test], cell_d['fill'])

  def test_e(self):
    ''' ReadNotFound will never find a bg ZZZ and return None
    '''
    ver = 0
    items = { 'fill':'#FFF', 'background':'#ZZZ', 'opacity':1.0 }
    self.assertFalse(self.p.readPid(ver, items))

  def test_f(self):
    ''' ReadWithItems get pid from items for ver: htmstarter 
    '''
    items = { 'fill':'#FFF', 'background':'#FF0', 'opacity':1.0 }
    pid = self.p.readPid(ver=3, color=items)
    self.assertEqual(pid, 49)

  def test_g(self):
    ''' selfet randomly to generate new palette
    '''
    self.p = Palette(ver=1) # universal
    self.p.loadPalette()
    cell = self.p.generate_any()
    #self.pp.pprint(f"c {cell}")
    self.assertEqual(len(cell.keys()), 3)
    self.assertTrue(
      tuple(
        [cell['fill'], 
        float(cell['fill_opacity']), 
        cell['bg']]
      ) 
      in self.p.palette
    )

  def test_h(self):
    ''' bad palette
    '''
    self.p = Palette(ver=999) # not done .. yet (:
    self.assertRaises(ValueError, self.p.loadPalette)

  def test_i(self):
    ''' palette should have opacity greather than 0
    '''
    self.p.loadPalette()
    [self.assertTrue((o >= 0.1 and o <= 1.0)) for o in self.p.opacity]

  def test_j(self):
    self.p.loadPalette()
    self.assertEqual(len(self.p.opacity), 4)
    
  def test_k(self):
    ''' items with pid used by View.read() 
    '''
    items = self.p.read_item(pid=4)
    self.assertEqual(items[0], '#C71585')

  def test_l(self):
    rink    = 'e444ac14353eca218fdf209b2578b498'
    palette = self.p.readStrokeFill(rink)
    self.assertEqual(4, len(palette))

  def test_m(self):
    pal = self.p.read_palette(8)
    self.assertEqual(43, len(pal))

  def test_o(self):
    ''' find the nearest opacity
    '''
    palette = (
      ['#FFA500', 0.9,    '#000'], 
      ['#CCC',    0.9, '#9ACD32'], 
      ['#C71585', 0.6,    '#FFF']
    )
    expected = [ (1, 187), (1, 531), (0.5, 159) ]
    for i in range(3):
      o, p = expected[i]
      op, pid = self.p.find_opacity(palette[i])
      self.assertEqual(o, op)
      self.assertEqual(p, pid)

  def test_p(self):
    ''' find colours in textfile that are missing from db
    '''
    palette = (
      ['#FFA500', 0.9,    '#xxx'],  # missing
      ['#yyy',    0.9, '#9ACD32'],  # missing
      ['#C71585', 0.6,    '#FFF']   # exists already
    )
    missing = self.p.colour_check(palette)
    self.assertEqual(2, len(missing))

'''
the 
end
'''
