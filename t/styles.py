#!/usr/bin/env python3
import os.path
import unittest
import pprint
from db import Styles
pp = pprint.PrettyPrinter(indent=2)

class TestStyles(unittest.TestCase):

  def setUp(self):
    self.s = Styles()

  def testCreate(self):
    ''' check bad values are Not inserted
    '''
    items = [''] 
    with self.assertRaises(IndexError):
      self.s.create(items)

  def testReadWithSid(self):
    ''' items with sid
    '''
    items = self.s.read(sid=4)
    self.assertEqual(items[0], '#FFF')

  def testReadWithItems1(self):
    ''' items with sid
    '''
    items = ['#FFF', '#CCC',  1.0, '#000',  0,  1,  0.5]
    sid = self.s.read(style=items)[0]
    self.assertEqual(sid, 1)

  def testReadWithItems5(self):
    ''' note that data cleaning stroke opacity to be less than 1.5 created duplicates
    '''
    items = ['#FFF', '#32CD32', 1.0, '#000', 0, 0, 1]
    sid = self.s.read(style=items)[0]
    self.assertEqual(sid, 435)

  def testReadNotFound(self):
    ''' will never find a stroke width: 100 
    '''
    items = ['#FFF', '#32CD32', 1.0, '#000', 100, 100, 0.5]
    sid = self.s.read(style=items)
    self.assertEqual(sid, None)

  def testValidateVer0(self):
    ''' both validation tests assume celldata format
        too much width
    '''
    data = self.s.defaults
    data['stroke_width'] = 100
    self.assertRaises(ValueError, self.s.validate, 'a', data)

  def testValidateVer1(self):
    ''' ver changes test to check palette matches
    '''
    self.s.set_spectrum(ver='colour45')
    data = self.s.defaults
    data['bg'] = '#FFA500'
    self.assertRaises(ValueError, self.s.validate, 'a', data)
    data['fill'] = '#FFF'
    self.assertRaises(ValueError, self.s.validate, 'a', data)

  def testGenerate(self):
    ''' select randomly from style database
    '''
    self.s.set_spectrum(ver='universal')
    for cell in ['a', 'b', 'c', 'd']:
      self.s.generate(cell, [1, 2, 3, 4])
    self.assertTrue('bg' in self.s.styles['a'])

  def testGenerateRandom(self):
    ''' randomly generate new attributes
    '''
    self.s.set_spectrum(ver='universal')
    for cell in ['a', 'b', 'c', 'd']:
      self.s.generate_any(cell) # lose control
    self.assertEqual(len(self.s.styles), 4) 

  ''' test cases
          recipe top
arpeggio  -      -
    koto  x      -
  spiral  -      x
soleares  x      x
  '''
  def testGenerateRecipeAndTopAll(self):
    ''' facing all for soleares
    '''
    self.s.set_spectrum(ver='colour45')
    topcells={ 'b': None, 'c': 'a', 'b': 'a', 'd': None, 'a': 'c', 'a': 'c' }
    for c in topcells.keys(): # mock of what b.read() will return 
      self.s.generate_all(c)
      self.assertTrue('bg' in self.s.styles[c])

  def testGenerateRecipeAndTopOne(self):
    ''' facing one for soleares
    '''
    #topcells={ 'b': None, 'c': 'a', 'b': 'a', 'd': None, 'a': 'c', 'a': 'c' }
    self.s.set_spectrum(ver='colour45')
    pairs = ('b', 'd')       # compass.one(axis)
    flip = {'north': 'south', 'south': 'north'}
    self.s.generate_one(pairs, flip)
    self.assertTrue('bg' in self.s.styles['b'])

  def testGenerateUniversal(self):
    ''' spiral has no recipe but does have top
        expect it to use default palette but still work
    '''
    self.s.set_spectrum(ver='universal')
    for cell in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p' ,'q', 'r']:
      self.s.generate(cell, [1])
    self.assertTrue('a' in self.s.styles)
