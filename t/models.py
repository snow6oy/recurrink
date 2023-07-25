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
    ''' key value pair with position as the key
    '''
    positions = self.b.read()
    self.assertEqual(positions[(2, 0)], 'a')

  def testGetCellWithTop(self):
    ''' can superimposed models list top cells as well?
    '''
    cells = self.b.read(output=list())
    self.assertEqual(len(cells), 4)
    bb = Blocks('spiral')
    cells = bb.read(output=list())
    self.assertEqual(len(cells), 24)

  def testGetTopByPosition(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    positions = self.b.read()
    cells = tuple()
    if type(positions[(1, 1)]) is tuple:
      cells = positions[(1, 1)]
    self.assertEqual(cells[1], 'a')
