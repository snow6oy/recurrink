#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from cell import CellData
from config import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.c = CellData(2) # colour45 inherit Stroke() class

  def test_a(self):
    ''' before writing SVG check TmpFile for human error
        (stroke width should not be 60)
    '''
    self.c.loadPalette()
    cells = config.cells['a']
    cells['color']['fill'] = '#zz'
    '''
    print(cells['color']['fill'])
    print(cells['color']['background'])
    cells = { 
      'a': { 
        'bg': '#DC143C', 'facing': 'east', 'fill': '#DC143C', 'fill_opacity': '1.0',
        'shape': 'line', 'size': 'large', 'stroke': '#DC143C', 'stroke_dasharray': 0,
        'stroke_opacity': '1', 'stroke_width': 60, 'top': True
      }
    }
    self.c.validate('a', cells) # does it raise an error
    self.assertRaises(Warning, self.c.validate, cells)
    '''

  def test_b(self):
    ''' commit new cells
        input data from conf/MODEL.yaml 
        fields: cell shape size facing top fill bg fo stroke sw sd so

      ['a','triangl','medium','west',False,'#FFF','#000',1.0,'#000',1,0,1]
    '''
    cell = CellData(ver=2)  # htmstarter
    data = config.cells
    self.assertFalse(cell.create(
      'e4681aa9b7aef66efc6290f320b43e55', 'a', data['a']
    ))


  def testGenerateOne(self):
    ''' called with axis cell generate along ONE axis
    '''
    self.c.generate(top=True, axis='east', facing='north')
    cell_a = self.c.data
    #pp.pprint(cell_a)
    self.assertEqual(len(cell_a.keys()), 11)
    self.assertEqual(cell_a['facing'], 'south')

  def testGenerateAll(self):
    ''' without axis cell generates facing all directions
    '''
    self.c.generate(top=False, facing_all=True)
    cell_b = self.c.data
    #pp.pprint(cell_b)
    self.assertEqual(len(cell_b.keys()), 11)
    self.assertEqual(cell_b['facing'], 'all')

  def testGenerateAny(self):
    ''' any cell is generated unless compass takes control
    '''
    self.c.generate(top=True)
    cell_c = self.c.data
    #pp.pprint(cell_c)
    self.assertEqual(len(cell_c.keys()), 11)

  def testRead(self):
    pass
'''
the
end
'''


