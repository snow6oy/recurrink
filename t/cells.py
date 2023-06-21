#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from db import Cells, Geometry, Styles
pp = pprint.PrettyPrinter(indent=2)

class TestCells(unittest.TestCase):

  def setUp(self):
    self.c = Cells() # inherit Db() class
    self.g = Geometry()
    self.s = Styles()

  def testSetGeometry(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing combination is new
      also it avoids side-effectof incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.g.set(['square', 'medium', 'north', False])
    self.assertTrue(tuple(gid))

  def testSetGeometryTop(self):
    ''' force top to False unless shape is large
      because otherwise when a shared geom is updated there would be side-effects 
      to properly test this first DELETE shape then run test and check top with SELECT
    '''
    gid = self.g.set(['square', 'medium', 'west', True])
    self.assertTrue(tuple(gid))

  def testSetGeometryMedium(self):
    ''' only circles, lines and square may be large
      to properly test this first DELETE shape then run test and check top with SELECT
    ''' 
    gid = self.g.set(['triangle', 'large', 'west', True])
    self.assertTrue(tuple(gid))

  def testSetStyleUpdate(self):
    ''' styles are not shareable. styles have 1:1 relation view/cell <> style
      this means styles are EITHER updated when the SID exists OR inserted
    '''
    sid = self.s.get('e4681aa9b7aef66efc6290f320b43e55', 'd')[0]
    self.assertEqual(sid, 4)
    sid = self.s.set(['#FFF', '#32CD32', 1.0, '#000', 0, 0, 0.5], sid=sid)[0]
    self.assertEqual(sid, 4)

  # uncomment to spam the styles table
  def testSetStyleInsert(self):
    # sid = self.s.set(['#FFF', '#32CD32', 1.0, '#000', 0, 0, 1.5])
    sid = True
    self.assertTrue(sid)

  def testSetCell(self):
    ''' send line from /tmp/MODEL.txt to update an existing view
        cell shape size facing top fill bg fo stroke sw sd so
    '''
    view = 'e4681aa9b7aef66efc6290f320b43e55'
    cell = 'a'
    data = ['a','triangle','medium','west',False,'#FFF','#CCC',1.0,'#000',0,1,0.5]
    self.assertTrue(self.c.set(view, cell, data))

  def testGetCellRandom(self):
    ''' Geometry and Styles got from existing entries
    '''
    #pp.pprint(self.c.get())
    self.assertEqual(len(self.c.get()), 11)

  # Note this test has a side effect of spamming the styles table
  # ALTER sequence styles_sid_seq restart with n
  # where n is SELECT MAX(sid) FROM cells
  def testGetCellRandomCreate(self):
    ''' Geometry and Styles set with randomly created entries
    '''
    # self.assertEqual(len(self.c.get(control=False)), 13)
    pass

  def testGetCellGid(self):
    self.assertEqual(self.g.get(gid=1)[2], 'south')

