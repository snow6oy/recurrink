#!/usr/bin/env python3
import os.path
import unittest
import pprint
from cell import Palette
pp = pprint.PrettyPrinter(indent=2)

class TestPalette(unittest.TestCase):

  def setUp(self):
    self.p = Palette(ver=1)  # colour45 is default
    self.defaults = {
      'fill': '#FFF',
      'bg': '#CCC',
      'opacity':1.0,
      'shape':'triangl',  # Geometry validates before Palette
      'size':'medium', 
      'facing':'all'
    }

  def testReadWithPid(self):
    ''' items with pid used by View.read() 
    '''
    items = self.p.read_item(pid=4)
    self.assertEqual(items[0], '#C71585')

  def testReadWithItems(self):
    ''' get pid from items for ver: htmstarter 
    '''
    self.p = Palette(ver=2)
    items = ['#FFF', '#FF0',  1.0]
    pid = self.p.read_pid(palette=items)
    self.assertEqual(pid, 49)

  def testReadNotFound(self):
    ''' will never find a bg ZZZ
    '''
    items = ['#FFF', '#ZZZ', 1.0]
    pid = self.p.read_pid(palette=items)
    self.assertEqual(pid, None)

  def testLoadPalette(self):
    self.p.load_palette(ver=2)
    #pp.pprint(self.p.palette)
    for fill in [ '#FFF', '#000', '#F00', '#00F', '#FF0' ]:
      self.assertTrue(fill in self.p.fill)
    self.assertEqual(self.p.opacity, [1.0])
    self.assertEqual(self.p.complimentary['#FFF'], '#000')

  def testLoadPaletteOk(self):
    self.p = Palette(ver=0) # universal not done yet
    self.p.load_palette()
    #pp.pprint(self.p.palette)
    self.assertTrue(len(self.p.palette))

  def testLoadPaletteError(self):
    ''' bad palette
    '''
    self.p = Palette(ver=999) # not done .. yet (:
    self.assertRaises(ValueError, self.p.load_palette)

  def testOpacity(self):
    ''' palette should have opacity greather than 0
    '''
    self.p = Palette(ver=0) 
    self.p.load_palette()
    for o in self.p.opacity:
      #print(f"opacity {o}")
      self.assertTrue((o >= 0.1))


  ''' opaque palettes are valid because non-square shapes display background
      all fg/bg combinations are also valid even when fg and bg are the same
  '''
  def testValidateVer0(self):
    ''' validate fake bg value 
    '''
    #self.p.spectrum(['#CCC'], ['#FFF'], [1], None)
    self.p.load_palette()
    data = self.defaults
    data['bg'] = '#ZZZ'
    self.assertRaises(ValueError, self.p.validate, 'a', data)

  def testValidateVer1(self):
    ''' ver changes test to check palette matches
    '''
    self.p.load_palette()
    data = self.defaults
    data['bg'] = '#FFA500'
    self.assertRaises(ValueError, self.p.validate, 'a', data)
    data['fill'] = '#FFF'
    self.assertRaises(ValueError, self.p.validate, 'a', data)

  def testValidateVer2(self):
    ''' ver changes test to check palette Hunt The Moon starter kit
    '''
    self.p.load_palette()
    data = self.defaults
    data['bg'] = '#FFA500'
    self.assertRaises(ValueError, self.p.validate, 'a', data)
    data['fill'] = '#DC143C'
    self.assertRaises(ValueError, self.p.validate, 'a', data)
    #pp.pprint(self.p.palette)

  def testGenerateAny(self):
    ''' selfect randomly to generate new palette
    '''
    self.p = Palette(ver=0) # universal
    self.p.load_palette()
    cell = self.p.generate_any()
    pp.pprint(f"c {cell}")
    self.assertEqual(len(cell.keys()), 3)
    self.assertTrue(cell['fill'] in self.p.fill)
    self.assertTrue(cell['bg'] in self.p.backgrounds)
    self.assertTrue(cell['fill_opacity'] in self.p.opacity)

  def testGenerateOne(self):
    ''' randomly generate first cell of pair and then allocate complimentary to the second cell 
    '''
    self.p.load_palette(ver=1)
    pairs = ('b', 'd')       # compass.one(axis) for context
    cell_b = self.p.generate_one(ver=1)
    #pp.pprint(cell_b)
    cell_d = self.p.generate_one(ver=1, primary=cell_b)
    #pp.pprint(cell_d)
    test = cell_b['fill']
    self.assertEqual(self.p.complimentary[test], cell_d['fill'])
