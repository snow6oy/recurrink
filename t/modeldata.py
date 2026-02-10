import unittest
import pprint
from model import ModelData

class Test(unittest.TestCase):
  pp  = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.md   = ModelData() 
    self.mid = 2 # mambo

  def test_a(self):
    ''' read model
    '''
    models = self.md.modelRead()
    self.assertTrue(len(models))

  def test_b(self):
    ''' get model id
    '''
    nrc, mid = self.md.model('mambo')
    self.assertEqual(self.mid, mid)

  def test_c(self):
    ''' read blocks
    '''
    blocks = self.md.blocksRead(self.mid)
    #self.pp.pprint(blocks)
    self.assertEqual(144, len(blocks))

  def test_d(self):
    ''' write 1 position in mambo block

DELETE from blocks where cell = 'z';
    '''
    blocks = {(99, 0): ('z', None)}

    blocks = self.md.blocksWrite(self.mid, blocks)
    #self.pp.pprint(blocks)
    self.assertTrue(self.md.count)

  def test_e(self):
    ''' get default scale for model

[(2, 'z', None, 'C')] mid cell pair facing
not yet done the conf, this is still raw dbrows format
    '''
    conf = self.md.compassRead(self.mid)
    self.assertTrue(len(conf))

  def test_f(self):
    ''' write conf and then 

DELETE FROM compass WHERE mid=2 AND cell='z';
    '''
    conf = {'C': ['z']}
    conf = self.md.compassWrite(self.mid, conf)
    self.assertTrue(self.md.count)

  def test_g(self):
    ver  = 1 # uniball
    name = self.md.pens(ver)
    self.assertEqual('uniball', name)

  def test_h(self):
    ''' list model blocksize
    '''
    bsx, bsy = self.md.setBlocksize(mid=15)
    self.assertEqual((3, 2), (bsx, bsy))

  def test_i(self):
    ''' load positions for a model
    '''
    pos = self.md.blocks(mid=15) # model='soleares'
    cell_1_1 = pos[(1, 1)]
    self.assertEqual(cell_1_1[0], 'd')

  def test_j(self):
    ''' can superimposed models list top cells as well?
    '''
    pos = self.md.blocks(mid=15) # soleares
    self.assertEqual(len(pos), 6)
    pos = self.md.blocks(mid=8) # spiral
    self.assertEqual(len(pos), 18)

  def test_k(self):
    ''' key value pair with cells as the key and top as value
    '''
    positions = self.md.blocks(mid=15)
    for p in positions:
      cell, top = positions[p]
      if cell == 'b':
        self.assertFalse(top) # b has no top in soleares

  def test_l(self):
    ''' virtual top 
        cell: g model: marching band
        example of Virtual Top. A cell that exist only as a top cell
    '''
    pos = self.md.blocks(mid=16) # marchingband
    self.pp.pprint(pos)
    cell_g = [pos[p][0] for p in pos if pos[p][0] == 'g']
    self.assertFalse(cell_g)

  def test_m(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    pos = self.md.blocks(mid=15) # soleares
    #pp.pprint(pos)
    cells = tuple()
    if type(pos[(2, 0)]) is tuple:
      cells = pos[(2, 0)]
    self.assertEqual(cells[1], 'c')

'''
the
end
'''
