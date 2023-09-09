#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from db import Cells, Recipe
pp = pprint.PrettyPrinter(indent=2)

class TestCells(unittest.TestCase):

  def setUp(self):
    self.c = Cells() # inherit Db() class

  def testGenerateWithRecipe(self):
    ''' marchingband has Virtual Top
    '''
    r = Recipe('marchingband')
    topcells = { 'b': None, 'c': None, 'a': None, 'd': None, 'e': 'h', 'f': 'g' }
    celldata, mesg = self.c.generate(r, False, topcells=topcells)
    #pp.pprint(celldata)
    #print(mesg)
    self.assertEqual(len(celldata.keys()), 8)

  def testGenerateRandom(self):
    r = Recipe('zz')
    topcells = { 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None }
    celldata, mesg = self.c.generate(r, True, topcells=topcells)
    #pp.pprint(celldata)
    #print(mesg)
    self.assertEqual(len(celldata.keys()), 6)

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
