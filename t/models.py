#!/usr/bin/env python3

from model.data import ModelData
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.m = ModelData() 

  def test_1(self):
    ''' random model selection 
    '''
    #print(self.m.generate())
    self.assertTrue(self.m.generate())

  def test_4(self):
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

  def test_5(self):
    ''' get default scale for model
    '''
    scale = self.m.getScale('koto') 
    self.assertTrue(scale, 0.75)
