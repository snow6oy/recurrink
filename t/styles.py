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

  def testGenerate0(self):
    ''' default is to select randomly from sid
    '''
    items = self.s.generate(0)
    #pp.pprint(items)
    self.assertEqual(len(items), 7)

  def testGenerate1(self):
    ''' select randomly from style value
    '''
    items = self.s.generate(1)
    self.assertEqual(len(items), 7)

  def testReadWithSid(self):
    ''' items with sid
    '''
    items = self.s.read(sid=4)
    self.assertEqual(items[0], '#FFF')

  def testReadWithItems(self):
    ''' items with sid
    '''
    items = ['#FFF', '#CCC',  1.0, '#000',  0,  1,  0.5]
    sid = self.s.read(style=items)[0]
    self.assertEqual(sid, 1)
    items = ['#FFF', '#32CD32', 1.0, '#000', 0, 0, 1.5]
    sid = self.s.read(style=items)[0]
    self.assertEqual(sid, 5)

  def testReadNotFound(self):
    ''' will never find a stroke width: 100 
    '''
    items = ['#FFF', '#32CD32', 1.0, '#000', 100, 100, 0.5]
    sid = self.s.read(style=items)
    self.assertEqual(sid, None)

  ''' both validation tests assume cellrow format
      ALSO ver changes test but not palette
  '''
  def testValidateVer0(self):
    items = ['#FFF', '#32CD32', 1.0, '#000', 100, 100, 0.5]
    self.assertRaises(ValueError, self.s.validate, items)

  def testValidateVer1(self):
    items = ['#FFF', '#32CD32', 1.0, '#000', 100, 100, 0.5]
    validated = self.s.validate(items, ver=1)
    print(validated)

''' 
  # uncomment to spam the styles table
  def testSetStyleInsert(self):
    sid = True
    self.assertTrue(sid)

  def testMax(self):
    maxsid = self.s.read()
    self.assertTrue(type(int))
set(self, items=[], sid=None):
get(self, view=None, cell=None, rnd=False, sid=None):
add(self, items):

create(control, items=[]
read(sid):  # view and cell move to cells
update(control, items=[], sid=None):
delete(self, sid)
_validate(items):
'''
