#!/usr/bin/env python3
import os.path
import unittest
import pprint
from cell import Palette
from palette import PaletteMaker
pp = pprint.PrettyPrinter(indent=2)

class TestPalette(unittest.TestCase):

  def setUp(self):
    self.p = Palette(ver=1)  # colour45 is default
    self.pmk = PaletteMaker()
    self.defaults = {
      'fill': '#FFF',
      'bg': '#CCC',
      'fill_opacity':1.0,
      'shape':'triangl',  # Geometry validates before Palette
      'size':'medium', 
      'facing':'all'
    }

  def test_0(self):
    p0 = Palette(ver=0)
    p0.load_palette()
    data = self.defaults
    data['shape'] = 'circle'  # pass geom
    data['fill'] = '#4B0082' 
    data['bg'] = '#CCC'
    data['stroke_opacity'] = None  # skip stroke
    data['fill_opacity'] = 0.7     # fail palette
    #pp.pprint(data)
    self.assertRaises(ValueError, p0.validate, 'a', data)

  def test_1(self):
    ''' Load Palette
    '''
    p = Palette(ver=2)
    p.load_palette(ver=2)
    #print(len(p.palette))
    #pp.pprint(p.palette)
    self.assertTrue(len(p.palette), 25)
    self.assertEqual(p.opacity, [1.0])
    self.assertEqual(p.complimentary['#FFF'], '#FFF')

  def test_2(self):
    ''' Generate One randomly generate first cell of pair and then allocate complimentary to the second cell 
    '''
    self.p.load_palette(ver=1)
    pairs = ('b', 'd')       # compass.one(axis) for context
    cell_b = self.p.generate_one(ver=1)
    #pp.pprint(cell_b)
    cell_d = self.p.generate_one(ver=1, primary=cell_b)
    #pp.pprint(cell_d)
    test = cell_b['fill']
    self.assertEqual(self.p.complimentary[test], cell_d['fill'])

  def test_3(self):
    ''' run some tests to see if complimentary relations exist
    DC143C crimson #C71585 mediumvioletred #FFA500 orange #32CD32 limegreen #4B0082 indigo
    '''
    expected = {
      '#dc143c': '#14dcb4', 
      '#c71585': '#15c756',
      '#ffa500': '#005aff',
      '#32cd32': '#cd32cd',
      '#4b0082': '#378200',
      '#ff0000': '#00ffff',
      '#ffff00': '#0000ff',
      '#0000ff': '#fffe00',
      '#ffffff': '#ffffff',
      '#000000': '#000000'
    }
    [self.assertEqual(expected[f], self.pmk.secondary(f)) for f in ['#dc143c', '#c71585', '#ffa500' ,'#32cd32', '#4b0082']]
    [self.assertEqual(expected[f], self.pmk.secondary(f)) for f in ['#ff0000', '#ffff00', '#0000ff' ,'#ffffff', '#000000']]

  def test_4(self):
    ''' find the nearest opacity
    '''
    ver = 0
    palette = (['#FFA500', 0.9, '#000'], ['#CCC', 0.9, '#9ACD32'], ['#C71585', 0.6, '#FFF'])
    expected = [ (1, 187), (1, 531), (0.5, 159) ]
    for i in range(3):
      #print(i)
      o, p = expected[i]
      op, pid = self.pmk.find_opacity(ver, palette[i], self.p)
      self.assertEqual(o, op) 
      self.assertEqual(p, pid) 

  def test_5(self):
    ''' ReadNotFound will never find a bg ZZZ
    '''
    ver = 0
    items = ['#FFF', '#ZZZ', 1.0]
    self.assertRaises(ValueError, self.p.read_pid, ver, items)

  def test_6(self):
    ''' ReadWithItems get pid from items for ver: htmstarter 
    '''
    self.p = Palette(ver=2)
    items = ['#FFF', '#FF0',  1.0]
    pid = self.p.read_pid(ver=2, palette=items)
    self.assertEqual(pid, 49)

  ''' opaque palettes are valid because non-square shapes display background
      all fg/bg combinations are also valid even when fg and bg are the same
  '''
  def test_7(self):
    ''' validate fake bg value 
    '''
    #self.p.spectrum(['#CCC'], ['#FFF'], [1], None)
    self.p.load_palette()
    data = self.defaults
    data['bg'] = '#ZZZ'
    self.assertRaises(ValueError, self.p.validate, 'a', data)

  def test_8(self):
    ''' ver changes test to check palette Hunt The Moon starter kit
    '''
    self.p = Palette(ver=2)
    self.p.load_palette()
    data = self.defaults
    data['bg'] = '#FFA500'
    self.assertRaises(ValueError, self.p.validate, 'a', data)
    data['fill'] = '#DC143C'
    self.assertRaises(ValueError, self.p.validate, 'a', data)

  def test_9(self):
    ''' FFF CCC 1. combination does not exist in jeb
    '''
    self.p = Palette(ver=3)
    self.p.load_palette()
    #pp.pprint(self.p.palette)
    self.assertRaises(ValueError, self.p.validate, 'a', self.defaults)

  def test_10(self):
    ''' selfect randomly to generate new palette
    '''
    self.p = Palette(ver=0) # universal
    self.p.load_palette()
    cell = self.p.generate_any()
    #pp.pprint(f"c {cell}")
    self.assertEqual(len(cell.keys()), 3)
    self.assertTrue(tuple([cell['fill'], float(cell['fill_opacity']), cell['bg']]) in self.p.palette)

  def test_11(self):
    ''' gridsize converts palette length into a rectangle
        so that tuple entries are displayed in three
        NOTE that int() is used instead of round() because round() can round up
        and that gives a NASTY index out of range error
    '''
    lenpal = [8, 24, 13, 33, 25, 60, 296]
    expected = [(6, 4, 0), (9, 8, 0), (6, 7, 5), (12, 9, 11), (9, 9, 8), (15, 12, 0), (30, 30, 24)]

    for i, lp in enumerate(lenpal):
      self.assertEqual(self.pmk.gridsize(3, lp), expected[i])

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
    p0 = Palette(ver=0) 
    p0.load_palette()
    [self.assertTrue((o >= 0.1 and o <= 1.0)) for o in p0.opacity]
    #pp.pprint(p0.opacity)
    p1 = Palette(ver=1)
    p1.load_palette()
    #pp.pprint(p1.opacity)
    self.assertEqual(len(p1.opacity), 3)
    p2 = Palette(ver=2)
    p2.load_palette()
    self.assertEqual(len(p2.opacity), 1)

  def testReadWithPid(self):
    ''' items with pid used by View.read() 
    '''
    items = self.p.read_item(pid=4)
    self.assertEqual(items[0], '#C71585')
