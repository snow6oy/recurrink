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
    ''' does not include record created by test_c
DELETE FROM colors WHERE ver = 4 AND penam = 'zz';
    '''
    pen_count = self.bd.colorsRead(self.ver)
    self.assertEqual(30, len(pen_count))

  def test_c(self):
    ''' add one row to the colors table
        99 is not a valid version
        but colorsWrite ignores it anyway and forces new ver
    '''
    data = dict()
    data['#999999'] = 'zz'
    colors = self.bd.colorsWrite(data, self.ver)
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
    mid      = 1
    created  = None
    pubdate  = None 
    self.bd.rinksWrite(self.rinkid, mid, self.ver, 90, 0.4)
    self.assertTrue(self.bd.count)

  def test_f(self):
    ''' read rink created by test_e
    rink = self.bd.rinksRead(self.rinkid)
    '''
    rink = self.bd.rinks(self.rinkid)
    self.assertEqual(1, rink[0]) # zzz rink has model id: 1

  def test_g(self):
    ''' update rink to use new pen
    '''
    mid      = 1
    new_ver  = 6
    created  = None
    pubdate  = None 
    rinkdata = [mid, new_ver, 90, 0.4, created, pubdate]
    # None, None created published
    self.bd.rinks(self.rinkid, rinkdata)
    self.assertTrue(self.bd.count)

  def test_h(self):
    ''' get factor for rink
    '''
    rink  = self.bd.rinks('6c9eab748082c458621722ab3cb684ec')
    self.assertTrue(0.5, rink[3])


'''
the
end
'''
