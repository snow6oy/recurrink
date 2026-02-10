import unittest
import pprint
from block import BlockData

class Test(unittest.TestCase):
  ''' test_c and test_e create a fake entry
      clean the entry before re-test
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.bd     = BlockData()
    self.ver    = 4 # stabilo68 new ver
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' # fake rink
    #self.b = BlockData('soleares') 

  def test_a(self):
    # send empty list to avoid creating unwanted records
    colors = self.bd.colors(self.ver, colors=list())
    self.assertFalse(self.bd.count)

  def test_b(self):
    pen_count = self.bd.colorsRead(self.ver)
    self.assertEqual(30, len(pen_count))

  def test_c(self):
    ''' 99 is not a valid value 
        but colorsWrite ignores it anyway and forces new ver

DELETE FROM colors WHERE ver = 4 AND penam = 'zz';
    '''
    colors = [[99, '#999999', 'zz']]
    colors = self.bd.colorsWrite(colors, self.ver)
    self.assertEqual(1, self.bd.count)

  def test_d(self):
    old_ver = 11
    new_ver = self.bd.version(old_ver)
    self.assertEqual(4, new_ver)

  def test_e(self):
    ''' create fake rink
        meta is based on data retrieved from db1

DELETE FROM rinks WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz';
    '''
    mid  = 1
    date = [None, None] # created published
    rink = self.bd.rinksWrite(self.rinkid, mid, self.ver, date, 90, 1)
    self.assertEqual(7, len(rink))

  def test_f(self):
    rink = self.bd.rinksRead(self.rinkid)
    self.assertEqual(1, rink[1]) # fake rink has model id: 1

'''
the
end
'''
