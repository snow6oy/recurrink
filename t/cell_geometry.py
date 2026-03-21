#!/usr/bin/env python3
import os.path
import unittest
import pprint
from cell.init import Geometry

class Test(unittest.TestCase):
  ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted 
      when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL 
      by anticipating UniqueViolation 

      geometry.generateOne(axis, top, facing)
      geometry.generateFacingCentre(top)
      geometry.generateFacingAny(top)

  '''
  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.g = Geometry()

  def test_a(self):
    ''' Generate Any direction
    '''
    geom = self.g.generateFacingAny()  
    items = list(geom.keys())
    self.assertEqual(len(items), 4)

  def test_b(self):
    ''' cells must face all directions for allocation pool to generate output
    '''
    geom = self.g.generateFacingCentre()
    self.assertEqual(geom['facing'], 'C')

  def test_c(self):
    ''' after compass pair is applied 
        cells b and d should be symmetrical on east-west axis
    '''
    pair = ('b', 'd')  # soleares compass, just for context
    cell_b = self.g.generateOne(axis='E', top=False, facing=None)
    b_facing = cell_b['facing']
    self.assertTrue(b_facing in ['N', 'S'])
    cell_d = self.g.generateOne(axis='E', top=False, facing=b_facing)
    d_facing = cell_d['facing'] 
    self.assertTrue(b_facing != d_facing)

'''
the
end
'''
