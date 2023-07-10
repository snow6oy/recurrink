#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from db import Geometry
pp = pprint.PrettyPrinter(indent=2)

class TestGeometry(unittest.TestCase):

  def setUp(self):
    self.g = Geometry()

  def testGenerate0(self):
    items = self.g.generate(0)
    self.assertTrue(len(items))

  def testCreate(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing combination is new
      also it avoids side-effectof incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.g.create(['square', 'medium', 'north', False])
    self.assertTrue(int(gid))

  def testValidate1(self):
    ''' force top to False unless shape is large
    '''
    geom = ['square', 'medium', 'west', True]
    self.assertFalse(self.g.validate(geom)[3])

  def testValidate2(self):
    ''' only circles, lines and square may be large
    ''' 
    items = ['triangl', 'large', 'west', True]
    self.assertEqual(self.g.validate(items)[1], 'medium')

  def testValidate3(self):
    a = ['triangl', 'medium', 'all', False]
    self.assertEqual(self.g.validate(a)[2], 'north')
