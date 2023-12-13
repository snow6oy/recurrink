#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from cell import Geometry
pp = pprint.PrettyPrinter(indent=2)

class TestGeometry(unittest.TestCase):
  ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL by anticipating UniqueViolation 
  '''
  def setUp(self):
    self.g = Geometry()

  def testReadTop(self):
    ''' number of top entries should be even
    '''
    cells = self.g.read(top=False)
    top = self.g.read(top=True)
    #pp.pprint(top)
    self.assertEqual(len(cells), len(top))

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

  def testGenerateAny(self):
    geom = self.g.generate_any()  
    items = list(geom.keys())
    self.assertEqual(len(items), 4)

  def testGenerateAll(self):
    ''' cells must face all directions for allocation pool to generate output
    '''
    geom = self.g.generate_all()
    self.assertEqual(geom['facing'], 'all')

  def testGenerateOne(self):
    ''' after compass pair is applied cells b and d should be symmetrical on east-west axis
    '''
    pair = ('b', 'd')  # soleares compass, just for context
    cell_b = self.g.generate_one(axis='east', top=False, facing=None)
    b_facing = cell_b['facing']
    self.assertTrue(b_facing in ['north', 'south'])
    cell_d = self.g.generate_one(axis='east', top=False, facing=b_facing)
    d_facing = cell_d['facing'] 
    self.assertTrue(b_facing != d_facing)
