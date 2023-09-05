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

  def testGenerateNotRandom(self):
    items = self.g.generate(False)  
    pp.pprint(items)
    self.assertTrue(len(items))

  def testReadAll(self):
    items = self.g.read()
    facing_all = [i for i in items if i[2] == 'all']
    #pp.pprint(facing_all)
    self.assertEqual(len(facing_all), 14)

  def testRead(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.g.read(geom=['square', 'medium', 'all', False])[0]
    self.assertTrue(int(gid))

  ''' force top to False unless shape is large
  def testValidate1(self):
    geom = ['square', 'medium', 'west', True]
    self.assertFalse(self.g.validate(geom)[3])
  '''
  def testValidate2(self):
    ''' only circles, lines and square may be large
    ''' 
    data = {'shape':'triangl', 'size':'large', 'facing':'west'}
    self.assertRaises(ValueError, self.g.validate, 'a', data)

  def testValidate3(self):
    ''' triangl cannot face all
    '''
    data = {'shape':'triangl', 'size':'medium', 'facing':'all'}
    self.assertRaises(ValueError, self.g.validate, 'a', data)

  def testFacingAll(self):
    ''' after recipe is applied cells b and d should be symmetrical on east-west axis
    '''
    self.g.celldata = { 
      'a': { 'facing': 'south', 'shape': 'triangle', 'size': 'medium', 'top': False },
      'c': { 'facing': 'south', 'shape': 'diamond', 'size': 'medium', 'top': False}
    }
    self.g.facing_all(['a', 'c'])  # send soleares recipe
    self.assertEqual(self.g.celldata['a']['facing'], 'all')
    self.assertEqual(self.g.celldata['c']['facing'], 'all')

  def testFacingOne(self):
    ''' after recipe is applied cells b and d should be symmetrical on east-west axis
    '''
    self.g.celldata = { 
      'b': { 'facing': 'east', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False},
      'd': { 'facing': 'south', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False}
    }
    recipe = [('b', 'd')]  # soleares recipe
    self.g.facing_one(recipe, { 'north': 'south', 'south': 'north' })
    #pp.pprint(self.g.celldata)
    self.assertTrue(self.g.celldata['b']['facing'] in ['north', 'south'])
