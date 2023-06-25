#!/usr/bin/env python3

''' 
set(self, items=[], sid=None):
get(self, view=None, cell=None, rnd=False, sid=None):
add(self, items):

create(control, items=[]
read(sid):  # view and cell move to cells
update(control, items=[], sid=None):
delete(self, sid)
_validate(items):
'''
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

  def testRead(self):
    ''' items with sid
    '''
    items = self.s.read(sid=4)
    self.assertEqual(items[0], '#FFF')

  def testMax(self):
    ''' max sid 
    '''
    maxsid = self.s.read()
    self.assertTrue(type(int))

  def testUpdate(self):
    items = ['#FFF', '#32CD32', 1.0, '#000', 0, 0, 0.5]
    sid = 4
    error = self.s.update(sid, items)
    self.assertFalse(error)

  # uncomment to spam the styles table
  def testSetStyleInsert(self):
    # sid = self.s.set(['#FFF', '#32CD32', 1.0, '#000', 0, 0, 1.5])
    sid = True
    self.assertTrue(sid)
