#!/usr/bin/env python3

from recurrink import Models, Blocks
import unittest

class TestModels(unittest.TestCase):

  def setUp(self):
    self.m = Models()
    self.b = Blocks('soleares') # inherit Db() class

  def testListModel(self):
    self.assertTrue('soleares' in self.m.get(output='list'))

  def testLoadModel(self):
    self.assertEqual(self.m.get(model='soleares')[1][1], 'd')
