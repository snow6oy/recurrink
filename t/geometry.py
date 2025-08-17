#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from cell.data import Geometry
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):
  ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted 
      when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL 
      by anticipating UniqueViolation 
  '''
  def setUp(self):
    self.g = Geometry()

  def test_a(self):
    ''' number of top entries
        gnomons are never on top
    '''
    top = self.g.read(top=True)
    self.assertEqual(27, len(top))

  def test_b(self):
    ''' test the newest geom that was randomly generated and added to the db
    '''
    geom = self.g.read(gid=70)
    self.assertEqual(geom, ('line', 'medium', 'W', True))

  def test_c(self):
    ''' only circles, lines and square may be large
    ''' 
    data = {'shape':'triangl', 'size':'large', 'facing':'W'}
    self.assertRaises(ValueError, self.g.validate, 'a', data)

  def test_d(self):
    ''' triangl cannot face all
    '''
    data = {'shape':'triangl', 'size':'medium', 'facing':'C'}
    self.assertRaises(ValueError, self.g.validate, 'a', data)

  def test_d(self):
    ''' Generate Any direction
    '''
    geom = self.g.generate_any()  
    items = list(geom.keys())
    self.assertEqual(len(items), 4)

  def test_e(self):
    ''' cells must face all directions for allocation pool to generate output
    '''
    geom = self.g.generate_all()
    self.assertEqual(geom['facing'], 'C')

  def test_f(self):
    ''' after compass pair is applied 
        cells b and d should be symmetrical on east-west axis
    '''
    pair = ('b', 'd')  # soleares compass, just for context
    cell_b = self.g.generate_one(axis='E', top=False, facing=None)
    b_facing = cell_b['facing']
    self.assertTrue(b_facing in ['N', 'S'])
    cell_d = self.g.generate_one(axis='E', top=False, facing=b_facing)
    d_facing = cell_d['facing'] 
    self.assertTrue(b_facing != d_facing)

'''
the
end
'''
