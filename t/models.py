#!/usr/bin/env python3

from db import Models, Blocks
import unittest

class TestModels(unittest.TestCase):

  def setUp(self):
    self.m = Models()
    self.b = Blocks('soleares') # inherit Db() class

  def testListModel(self):
    self.assertTrue('soleares' in self.m.get(output='list'))

  def testLoadModel(self):
    self.assertEqual(self.m.get(model='soleares')[1][1], 'd')

  def testGetCellByPosition(self):
    ''' model with a line a, x, x a will appear in result as { a: { positions: [[0,0], [3,0] }}
    '''
    b = Blocks('soleares')
    positions = b.get()
    self.assertEqual(positions[(2, 0)], 'a')
