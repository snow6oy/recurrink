#!/usr/bin/env python3

from block.data import BlockData
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.b = BlockData('soleares') 

  def test_4(self):
    ''' key value pair with position as the key
    '''
    model = 'soleares'
    #xy = self.b.read(model=model)[2]
    positions = self.b.readPositions(model)
    #pp.pprint(positions)
    self.assertEqual(positions[(1, 1)][0], 'd')

  def test_5(self):
    ''' can superimposed models list top cells as well?
    '''
    cells = self.b.readPositions('soleares', output=list())
    self.assertEqual(len(cells), 4)
    cells = self.b.readPositions('spiral', output=list())
    self.assertEqual(len(cells), 24)

  def test_6(self):
    ''' key value pair with cells as the key and top as value
    '''
    positions = self.b.readPositions('soleares')
    for p in positions:
      cell, top = positions[p]
      if cell == 'b':
        self.assertFalse(top) # b has no top in soleares

  def test_7(self):
    ''' virtual top 
        cell: g model: marching band
        example of Virtual Top. A special cell that exist only as a top cell
    '''
    uniqcells = self.b.readPositions('marchingband', output=list())
    topcells = self.b.topcells('marchingband')
    [self.assertTrue(tc in uniqcells) for tc in topcells]

  def test_8(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    positions = self.b.readPositions('soleares')
    #pp.pprint(positions)
    cells = tuple()
    if type(positions[(2, 0)]) is tuple:
      cells = positions[(2, 0)]
    self.assertEqual(cells[1], 'c')

  def test_10(self):
    ''' top or not
    '''
    model = 'soleares'
    uniqcells = self.b.readPositions(model, output=list())
    topcells = self.b.topcells(model)
    self.assertEqual(topcells, ['a', 'c'])


  def test_9(self):
    ''' top or not with four four
    '''
    model = 'fourfour'
    uniqcells = self.b.readPositions(model, output=list())
    topcells = self.b.topcells(model)
    self.assertEqual(topcells[0], 'd')
