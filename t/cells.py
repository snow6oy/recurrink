#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from db import Cell, Recipe
pp = pprint.PrettyPrinter(indent=2)

class TestCells(unittest.TestCase):

  def setUp(self):
    self.c = Cell('colours45') # inherit Db() class

  def testGenerate(self):
    ''' default generate selects from db
    '''
    self.c.generate('a', top=False)
    cell_a = self.c.g.geom['a'] | self.c.s.styles['a']
    #pp.pprint(cell_a)
    self.assertEqual(len(cell_a.keys()), 11)

  def testGenerateRandom(self):
    ''' only styles are random 
    '''
    self.c.generate_any('z', top=True)
    #pp.pprint(self.c.s.styles)
    s = self.c.s.styles['z']
    self.assertEqual(len(s.keys()), 7)

  def testRead(self):
    ''' styles are not shareable. styles have 1:1 relation view/cell <> style
      this means styles are EITHER updated when the SID exists OR inserted
    '''
    sid = self.c.read('e4681aa9b7aef66efc6290f320b43e55', 'd')[0]
    self.assertEqual(sid, 4)

  def testCreate(self):
    ''' send line from /tmp/MODEL.txt to update an existing view
        cell shape size facing top fill bg fo stroke sw sd so
    '''
    self.assertFalse(self.c.create(
      'e4681aa9b7aef66efc6290f320b43e55',
      ['a','triangl','medium','west',False,'#FFF','#CCC',1.0,'#000',0,1,0.5]
    ))

  def testTransform(self):
    pass

  def testValidate(self):
    ''' before writing SVG check TmpFile for human error
        (stroke opacity should not be 100)
    '''
    cells = { 
      'a': { 
        'bg': '#DC143C', 'facing': 'east', 'fill': '#4B0082', 'fill_opacity': '1.0',
        'shape': 'line', 'size': 'large', 'stroke': '#DC143C', 'stroke_dasharray': 0,
        'stroke_opacity': '100', 'stroke_width': 6, 'top': True
      }
    }
    #self.c.validate(cells) # does it raise an error
    self.assertRaises(ValueError, self.c.validate, cells)
