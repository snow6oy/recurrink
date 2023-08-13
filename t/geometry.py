#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from db import Geometry, Recipe
pp = pprint.PrettyPrinter(indent=2)

class TestGeometry(unittest.TestCase):

  def setUp(self):
    self.g = Geometry()

  def testGenerateNotRandom(self):
    items = self.g.generate(False)  
    self.assertTrue(len(items))

  def testTransform(self):
    ''' after recipe is applied cells b and d should be symmetrical on east-west axis
    '''
    cells = { 
      'a': { 'geom': { 
          'facing': 'south', 'shape': 'triangle', 'size': 'medium', 'stroke_width': 0, 'top': False }},
      'b': { 'geom': { 
          'facing': 'east', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False}},
      'c': { 'geom': { 
          'facing': 'south', 'shape': 'diamond', 'size': 'medium', 'stroke_width': 6, 'top': False}},
      'd': { 'geom': { 
          'facing': 'south', 'shape': 'line', 'size': 'large', 'stroke_width': 0, 'top': False}}
    }
    recipe = Recipe('soleares')
    data = self.g.transform(cells, recipe)
    pp.pprint(data)

  def testCreate(self):
    pass # avoid creating unwanted geometries

  def testRead(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing/top combination is new
      immutable avoids side-effect of incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.g.read(geom=['square', 'medium', 'all', False])[0]
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
