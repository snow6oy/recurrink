import unittest
import pprint
from block.data2 import BlockData2

class Test(unittest.TestCase):
  ''' test_c and test_e create a fake entry
      clean the entry before re-test
  '''


  def setUp(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    self.bd     = BlockData2()
    self.ver    = 4 # stabilo68 new ver
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' # fake rink

  def test_a(self):
    colors      = list() # empty to avoid creating unwanted records
    nrc, colors = self.bd.colors(colors, self.ver)
    self.assertFalse(nrc)

  def test_b(self):
    pen_count = self.bd.colorsRead(self.ver)
    self.assertEqual(30, pen_count)

  def test_c(self):
    ''' 99 is not a valid value 
        but colorsWrite ignores it anyway and forces new ver

DELETE FROM colors WHERE ver = 4 AND penam = 'zz';
    '''
    colors      = [[99, '#999999', 'zz']]
    nrc, colors = self.bd.colorsWrite(colors, self.ver)
    self.assertEqual(1, nrc)

  def test_d(self):
    old_ver = 11
    new_ver = self.bd.version(old_ver)
    self.assertEqual(4, new_ver)

  def test_e(self):
    ''' create fake rink
        meta is based on data retrieved from db1

DELETE FROM rinks WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz';
    '''
    mid       = 1
    meta      = [self.ver, None, None] # new_ver created published
    nrc, rink = self.bd.rinksWrite(self.rinkid, mid, meta, None, 0.4)
    #print(nrc, rink)
    self.assertEqual(7, len(rink))

  def test_f(self):
    rink = self.bd.rinksRead(self.rinkid)
    self.assertEqual(1, rink[1]) # fake rink has model id: 1

'''
the
end
'''
