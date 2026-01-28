import unittest
import pprint
from model.data2 import ModelData2

class Test(unittest.TestCase):

  def setUp(self):
    self.m   = ModelData2() 
    self.pp  = pprint.PrettyPrinter(indent=2)
    self.mid = 2 # mambo

  def test_a(self):
    ''' read model
    '''
    models = self.m.modelRead()
    self.assertTrue(len(models))

  def test_b(self):
    ''' get model id
    '''
    nrc, mid = self.m.model('mambo')
    self.assertTrue(mid)

  def test_c(self):
    ''' read blocks
    '''
    blocks = self.m.blocksRead(self.mid)
    #self.pp.pprint(blocks)
    self.assertEqual(144, len(blocks))

  def test_d(self):
    ''' write 1 position in mambo block

DELETE from blocks where cell = 'z';
    '''
    blocks = {(99, 0): ('z', None)}

    nrc, blocks = self.m.blocksWrite(self.mid, blocks)
    #self.pp.pprint(blocks)
    self.assertTrue(nrc)

  def test_e(self):
    ''' get default scale for model

[(2, 'z', None, 'C')] mid cell pair facing
not yet done the conf, this is still raw dbrows format
    '''
    conf = self.m.compassRead(self.mid)
    self.assertTrue(len(conf))


  def test_f(self):
    ''' write conf and then 

DELETE FROM compass WHERE mid=2 AND cell='z';
    '''
    conf      = {'C': ['z']}
    nrc, conf = self.m.compassWrite(self.mid, conf)

  def test_g(self):
    ver  = 1 # uniball
    name = self.m.pens(ver)
    self.assertEqual('uniball', name)
'''
the
end
'''
