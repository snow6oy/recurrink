#!/usr/bin/env python3

from db import Models, Blocks
import unittest

class TestModels(unittest.TestCase):

  def setUp(self):
    self.m = Models()
    self.b = Blocks('soleares') # inherit Db() class

  def testRndModel(self):
    #print(self.m.generate())
    self.assertTrue(self.m.generate())

  def testListModel(self):
    self.assertTrue('soleares' in self.m.read())

  def testLoadModel(self):
    cell_1_1 = self.m.positions(model='soleares')[1][1]
    self.assertEqual(cell_1_1, 'd')

  def testModelEntry(self):
    name = self.m.read(model='soleares')[0]
    self.assertEqual(name, 'soleares')

  def testGetCellByPosition(self):
    ''' model with a line a, x, x a will appear in result as { a: { positions: [[0,0], [3,0] }}
    '''
    positions = self.b.read()
    self.assertEqual(positions[(2, 0)], 'a')
