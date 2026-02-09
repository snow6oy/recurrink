import unittest
import pprint
from model import ModelData

class Test(unittest.TestCase):
  pp  = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.m   = ModelData() 
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
    self.assertEqual(self.mid, mid)

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

    blocks = self.m.blocksWrite(self.mid, blocks)
    #self.pp.pprint(blocks)
    self.assertTrue(self.m.count)

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
    conf = {'C': ['z']}
    conf = self.m.compassWrite(self.mid, conf)
    self.assertTrue(self.m.count)

  def test_g(self):
    ver  = 1 # uniball
    name = self.m.pens(ver)
    self.assertEqual('uniball', name)

  def test_h(self):
    ''' list model blocksize
    '''
    bsx, bsy = self.m.setBlocksize(mid=15)
    self.assertEqual((3, 2), (bsx, bsy))

  def test_i(self):
    ''' load positions for a model
    '''
    pos = self.m.positions(mid=15) # model='soleares'
    #pp.pprint(pos)
    cell_1_1 = pos[1][1]
    self.assertEqual(cell_1_1, 'd')
'''
the
end
'''
