#!/usr/bin/env python3
import unittest
import pprint
from cell import Strokes
pp = pprint.PrettyPrinter(indent=2)

class TestStrokes(unittest.TestCase):

  def setUp(self):
    self.s = Strokes(ver=2) # colour45
    self.defaults = {
      'fill': '#FFF',
      'width': 0,
      'dasharray': 0,
      'opacity':1.0,
      'shape':'triangl',  # Geometry validates before Palette
      'size':'medium',
      'facing':'all'
    }

  def testCreateFailOk(self):
    ''' check bad values are Not inserted
    '''
    items = [''] 
    with self.assertRaises(ValueError):
      self.s.create(items)

  def testCreateNotDuplicate(self):
    ''' check good values are Not duplicated
    '''
    sid = self.s.create(['#9ACD32', '9', '0', '1'])
    self.assertEqual(sid, 1)

  def testReadWithSid(self):
    ''' items with sid
    '''
    items = self.s.read(sid=4)
    self.assertEqual(items[0], '#FFF')

  def testReadWithItems(self):
    ''' items with sid
    '''
    items = [
      ['#FFF', 1.0, 0,  0.4],
      [None, 0, None, None],
      ['#000',8,1,1.0],
      ['#000',8,1,1.0],
      ['#FFF',9,0,1.0]]

    for i, expected in enumerate([20, None, 122, 122, 16]):
      sid = self.s.read_sid(strokes=items[i])
      self.assertEqual(sid, expected)

  def testReadNotFound(self):
    ''' will never find a stroke width: 100 
    '''
    items = ['#000', 100, 100, 0.5]
    sid = self.s.read_sid(strokes=items)
    self.assertEqual(sid, None)

  def testValidateVer(self):
    ''' validation tests assume spectrum has been set
        too much width
    '''
    self.s.load_palette()
    data = self.defaults
    data['width'] = 100
    data['bg'] = '#CCC'
    self.assertRaises(ValueError, self.s.validate, 'z', data)

  def test_0(self):
    ''' generateOne select stroke using complimentary palette OK
    '''
    self.s.load_palette(ver=3)
    #pp.pprint(self.s.complimentary)
    cell = self.s.generate_one(stroke={ 
      'stroke': '#0F0', 'stroke_width': 1, 'stroke_dasharray': 1, 'stroke_opacity': 1.0 
    })
    self.assertEqual(cell['stroke'], '#F0F')

  def test_1(self):
    ''' generateOne select stroke using complimentary palette FAIL 
    '''
    self.s.load_palette(ver=1)
    #pp.pprint(self.s.complimentary)
    cell = self.s.generate_one(stroke={ 
      'stroke': '#C71585', 'stroke_width': 1, 'stroke_dasharray': 1, 'stroke_opacity': 1.0 
    })
    self.assertEqual(cell['stroke'], '#000')

  def testGenerateAny(self):
    ''' randomly generate new attributes
    '''
    ver1 = ['#DC143C','#4B0082','#FFA500','#32CD32','#C71585','#9ACD32','#FFF','#000','#CD5C5C']
    for cell in ['a', 'b', 'c', 'd']:
      data = self.s.generate_any(ver=1) 
      if data['stroke']: # can be None
        self.assertTrue(data['stroke'] in ver1)  # multiple tests to avoid random good luck
    #pp.pprint(data)

  def testGenerateAnyV2(self):
    ''' opacity for v2 must equal 1
    '''
    for cell in ['a', 'b', 'c', 'd']:
      data = self.s.generate_any(ver=2) 
      #pp.pprint(data)
      if data['stroke']: # can be None
        self.assertEqual(data['stroke_opacity'], 1)  

  def testGenerateNew(self):
    ''' select randomly from stroke attributes
    '''
    s = Strokes(ver=2) 
    s.load_palette()
    #pp.pprint(s.palette)
    for cell in ['a', 'b', 'c', 'd']:
      data = s.generate_new()
      self.assertEqual(len(data), 4) 
