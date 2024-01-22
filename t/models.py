#!/usr/bin/env python3

from views import Models, Blocks, Compass
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

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
    pos = self.m.positions(model='soleares')
    #pp.pprint(pos)
    cell_1_1 = pos[1][1]
    self.assertEqual(cell_1_1, 'd')

  def testModelEntry(self):
    name = self.m.read(model='soleares')[0]
    self.assertEqual(name, 'soleares')

  def testGetCellByPosition(self):
    ''' key value pair with position as the key
    '''
    m = 'soleares'
    b = Blocks(m)
    xy = self.m.read(model=m)[2]
    positions = b.read()
    #pp.pprint(positions)
    self.assertEqual(positions[(1, 1)][0], 'd')

  def testGetCellWithTop(self):
    ''' can superimposed models list top cells as well?
    '''
    cells = self.b.read(output=list())
    self.assertEqual(len(cells), 4)
    bb = Blocks('spiral')
    cells = bb.read(output=list())
    self.assertEqual(len(cells), 24)

  def test_1(self):
    ''' key value pair with cells as the key and top as value
    '''
    positions = self.b.read()
    for p in positions:
      cell, top = positions[p]
      if cell == 'b':
        self.assertFalse(top) # b has no top in soleares

  def test_0(self):
    ''' virtual top 
        cell: g model: marching band
        example of Virtual Top. A special cell that exist only as a top cell
    '''
    b = Blocks('marchingband')
    uniqcells = b.read(output=list())
    topcells = b.topcells()
    [self.assertTrue(tc in uniqcells) for tc in topcells]

  def testGetTopByPosition(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    positions = self.b.read()
    #pp.pprint(positions)
    cells = tuple()
    if type(positions[(2, 0)]) is tuple:
      cells = positions[(2, 0)]
    self.assertEqual(cells[1], 'c')

  def testTopOrNot1(self):
    uniqcells = self.b.read(output=list())
    topcells = self.b.topcells()
    self.assertEqual(topcells, ['a', 'c'])

  def testTopOrNot2(self):
    ff = Blocks('fourfour')
    uniqcells = ff.read(output=list())
    topcells = ff.topcells()
    self.assertEqual(topcells[0], 'd')

  def testGetCompassOne(self):
    ''' lookup recipe for mirroring from model or None
    '''
    compass = Compass('timpani')
    pairs, axis = compass.one('j')  # j is on the northeast axis
    #print(pairs, axis)
    self.assertEqual(pairs[1], 'j')
    self.assertEqual(axis, 'northeast')

  def testGetCompassAll(self):
    ''' lookup recipe for mirroring from model or None
    '''
    compass = Compass('timpani')
    self.assertTrue(compass.all('k'))

  def testGetScale(self):
    scale = self.m.get_scale('koto') 
    self.assertTrue(scale, 0.75)
