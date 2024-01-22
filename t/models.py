#!/usr/bin/env python3

from views import Models, Compass
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

class TestModels(unittest.TestCase):

  def setUp(self):
    self.m = Models() # inherit Db() class from Blocks()
    # self.b = Blocks('soleares') 

  def test_0(self):
    ''' random model selection 
    '''
    #print(self.m.generate())
    self.assertTrue(self.m.generate())

  def test_1(self):
    ''' list model
    '''
    self.assertTrue('soleares' in self.m.read())

  def test_2(self):
    ''' load positions for a model
    '''
    pos = self.m.positions(model='soleares')
    # pp.pprint(pos)
    cell_1_1 = pos[1][1]
    self.assertEqual(cell_1_1, 'd')

  def test_3(self):
    ''' model entry
    '''
    name = self.m.read(model='soleares')[0]
    self.assertEqual(name, 'soleares')

  def test_4(self):
    ''' key value pair with position as the key
    '''
    model = 'soleares'
    xy = self.m.read(model=model)[2]
    positions = self.m.read_positions(model)
    #pp.pprint(positions)
    self.assertEqual(positions[(1, 1)][0], 'd')

  def test_5(self):
    ''' can superimposed models list top cells as well?
    '''
    cells = self.m.read_positions('soleares', output=list())
    self.assertEqual(len(cells), 4)
    cells = self.m.read_positions('spiral', output=list())
    self.assertEqual(len(cells), 24)

  def test_6(self):
    ''' key value pair with cells as the key and top as value
    '''
    positions = self.m.read_positions('soleares')
    for p in positions:
      cell, top = positions[p]
      if cell == 'b':
        self.assertFalse(top) # b has no top in soleares

  def test_7(self):
    ''' virtual top 
        cell: g model: marching band
        example of Virtual Top. A special cell that exist only as a top cell
    '''
    uniqcells = self.m.read_positions('marchingband', output=list())
    topcells = self.m.topcells('marchingband')
    [self.assertTrue(tc in uniqcells) for tc in topcells]

  def test_8(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    positions = self.m.read_positions('soleares')
    #pp.pprint(positions)
    cells = tuple()
    if type(positions[(2, 0)]) is tuple:
      cells = positions[(2, 0)]
    self.assertEqual(cells[1], 'c')

  def test_8(self):
    ''' top or not
    '''
    model = 'soleares'
    uniqcells = self.m.read_positions(model, output=list())
    topcells = self.m.topcells(model)
    self.assertEqual(topcells, ['a', 'c'])

  def test_9(self):
    ''' top or not with four four
    '''
    model = 'fourfour'
    uniqcells = self.m.read_positions(model, output=list())
    topcells = self.m.topcells(model)
    self.assertEqual(topcells[0], 'd')

  def test_10(self):
    ''' lookup recipe for mirroring from model or None
    '''
    compass = Compass('timpani')
    pairs, axis = compass.one('j')  # j is on the northeast axis
    #print(pairs, axis)
    self.assertEqual(pairs[1], 'j')
    self.assertEqual(axis, 'northeast')

  def test_11(self):
    ''' lookup recipe for mirroring from model or None
    '''
    compass = Compass('timpani')
    self.assertTrue(compass.all('k'))

  def test_12(self):
    ''' get default scale for model
    '''
    scale = self.m.get_scale('koto') 
    self.assertTrue(scale, 0.75)
