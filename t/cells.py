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

  def testGenerate0(self):
    ''' Geometry and Styles got from existing entries with default control 0
    '''
    #pp.pprint(self.c.generate(0))
    self.assertEqual(len(self.c.generate(0)), 11)

  def testGenerate1(self):
    ''' Geometry and Styles set with randomly created entries control 1
    '''
    self.assertEqual(len(self.c.generate(1)), 11)

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
