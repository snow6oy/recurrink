#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import os.path
import unittest
import pprint
from cell import CellData, Palette
from cell.minkscape import *
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.c = CellData(2) # colour45 inherit Stroke() class

  def test_a(self):
    ''' commit new cells
        input data from conf/MODEL.yaml 
        fields: cell shape size facing top fill bg fo stroke sw sd so

      ['a','triangl','medium','west',False,'#FFF','#000',1.0,'#000',1,0,1]
    '''
    cell = CellData(ver=3)  # htmstarter
    data = minkscape.cells
    self.assertFalse(cell.create(
      'e4681aa9b7aef66efc6290f320b43e55', 'a', data['a']
    ))

  def test_b(self):
    ''' before writing SVG check TmpFile for human error
        (stroke width should not be 60)
    '''
    cells = minkscape.cells
    cells['a']['color']['fill'] = '#zz'

    pal = Palette()
    pal.loadPalette(2)  # set uniqfill
    self.assertRaises(ValueError, pal.validate, 'a', cells['a'])

  def test_c(self):
    ''' without axis cell generates facing all directions
    '''
    self.c.generate(top=False, facing_all=True)
    cell_b = self.c.data
    #pp.pprint(cell_b)
    self.assertEqual(len(cell_b.keys()), 11)
    self.assertEqual(cell_b['facing'], 'C')

  def test_d(self):
    ''' any cell is generated unless compass takes control
    '''
    self.c.generate(top=True)
    cell_c = self.c.data
    #pp.pprint(cell_c)
    self.assertEqual(len(cell_c.keys()), 11)

  def test_e(self):
    ''' called with axis cell generate along ONE axis
    '''
    self.c.generate(top=True, axis='E', facing='N')
    cell_a = self.c.data
    #pp.pprint(cell_a)
    self.assertEqual(len(cell_a.keys()), 11)
    self.assertEqual(cell_a['facing'], 'S')

'''
the
end
'''
