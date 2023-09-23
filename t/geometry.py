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

  def testGenerate(self):
    items = [
      ('diamond', 'medium', 'north', False),
      ('diamond', 'medium', 'south', False),
      ('diamond', 'medium', 'east', False),
      ('diamond', 'medium', 'west', False)
    ]
    self.g.generate('a', items)  
    items = list(self.g.geom['a'].keys())
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
    ''' cells must face all directions for allocation pool to generate output
    '''
    items = [
      ('square', 'medium', 'all', False),
      ('diamond',  'medium', 'all', False)
    ]
    items = self.g.generate_all('a', False, items)  # send soleares compass
    self.g.generate_all('c', False, items)  # send soleares compass
    self.assertEqual(self.g.geom['a']['facing'], 'all')
    self.assertEqual(self.g.geom['c']['facing'], 'all')

  def testFacingOne(self):
    ''' after recipe is applied cells b and d should be symmetrical on east-west axis
    '''
    items = [
      ('diamond', 'medium', 'north', False),
      ('diamond', 'medium', 'south', False),
      ('diamond', 'medium', 'east', False),
      ('diamond', 'medium', 'west', False)
    ]
    pair = ('b', 'd')  # soleares compass
    self.g.generate_one(pair, 'east', False, items)
    b_facing = self.g.geom['b']['facing']
    d_facing = self.g.geom['d']['facing']
    self.assertTrue(b_facing in ['north', 'south'])
    self.assertTrue(b_facing != d_facing)
