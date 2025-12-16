#!/usr/bin/env python3

from block.data import Compass
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.compass = Compass('timpani')

  def test_a(self):
    ''' lookup recipe for mirroring from model or None
    '''
    pairs, axis = self.compass.one('j')  # j is on the northeast axis
    #print(pairs, axis)
    self.assertEqual(pairs[1], 'j')
    self.assertEqual(axis, 'NE')

  def test_b(self):
    ''' lookup recipe for mirroring from model or None
    '''
    self.assertTrue(self.compass.all('k'))
