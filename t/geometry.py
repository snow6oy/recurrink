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
    self.g.generate('a', False)  
    items = list(self.g.geom['a'].keys())
    self.assertEqual(len(items), 4)

  def testGenerateRandom(self):
    self.g.generate('a', True)  
    items = list(self.g.geom['a'].keys())
    #print(items)
    self.assertEqual(len(items), 4)

  def testReadAll(self):
    items = self.g.read()
    #pp.pprint(items)
    facing_all = [i for i in items if i[2] == 'all']
    #pp.pprint(facing_all)
    self.assertEqual(len(facing_all), 14)

  def testReadTop(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL by anticipating UniqueViolation '''
    cells = self.g.read(top=False)
    #pp.pprint(cells)
    self.assertTrue(len(cells))

  def testReadGid(self):
    ''' test the newest geom that was randomly generated and added to the db
    '''
    geom = self.g.read(gid=70)
    self.assertEqual(geom, ('line', 'medium', 'west', True))

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
    ''' after recipe is applied cells a and c should face all directions
    '''
    self.g.celldata = { 
      'a': { 'facing': 'south', 'shape': 'triangle', 'size': 'medium', 'top': False },
      'c': { 'facing': 'south', 'shape': 'diamond', 'size': 'medium', 'top': False}
    }
    self.g.generate_facing_all(['a', 'c'])  # send soleares recipe
    self.assertEqual(self.g.geom['a']['facing'], 'all')

  def testFacingOne(self):
    ''' after recipe is applied cells b and d should be symmetrical on east-west axis
    '''
    self.g.celldata = { 
      'b': { 'facing': 'east', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False},
      'd': { 'facing': 'south', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False}
    }
    recipe = [('b', 'd')]  # soleares recipe
    self.g.generate_facing_pairs(recipe, { 'north': 'south', 'south': 'north' })
    b_facing = self.g.geom['b']['facing']
    d_facing = self.g.geom['d']['facing']
    self.assertTrue(b_facing in ['north', 'south'])
    self.assertTrue(b_facing != d_facing)
