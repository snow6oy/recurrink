import unittest
import pprint
from model import ModelData

class Test(unittest.TestCase):
  pp  = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.md      = ModelData() 
    self.mid     = 2 # mambo
    self.VERBOSE = True

  def test_a(self):
    ''' read model
    '''
    models = self.md.modelRead()
    self.assertTrue(len(models))

  def test_b(self):
    ''' list model
    '''
    self.assertTrue('soleares' in self.md.modelRead())

  def test_c(self):
    ''' load positions for a model
    '''
    mid = 15 # soleares
    pos = self.md.blocksRead(mid)
    if self.VERBOSE: self.pp.pprint(pos)
    cell_1_1 = pos[(1, 1)]
    self.assertEqual('d', cell_1_1[0])

  def test_d(self):
    ''' model id from name
    '''
    mid = self.md.model(name='soleares')
    self.assertEqual(15, mid)

  def test_e(self):
    ''' also see test_f

    '''
    pens = self.md.pens()
    self.assertEqual('uniball', pens[1])

  def test_f(self):
    ''' visual test of block

        careful with test_i
    '''
    pretty = self.md.positionString(self.mid)
    self.pp.pprint(pretty)

  def test_g(self):
    ''' get model id
    '''
    mid = self.md.model('mambo')
    self.assertEqual(self.mid, mid)

  def test_h(self):
    ''' read blocks

DELETE from blocks where mid = 2 and cell = 'z';
    '''
    blocks = self.md.blocksRead(self.mid)
    #self.pp.pprint(blocks)
    self.assertEqual(144, len(blocks))

  def test_i(self):
    ''' write 1 position in mambo block

    '''
    blocks = {(99, 0): ('z', None)}

    blocks = self.md.blocksWrite(self.mid, blocks)
    #self.pp.pprint(blocks)
    self.assertTrue(self.md.count)

  def test_j(self):
    ''' get default scale for model

[(2, 'z', None, 'C')] mid cell pair facing
not yet done the conf, this is still raw dbrows format
    '''
    conf = self.md.compassRead(self.mid)
    self.assertTrue(len(conf))

  def test_k(self):
    ''' write conf and then 

DELETE FROM compass WHERE mid=2 AND cell='z';
    '''
    conf = {'C': ['z']}
    conf = self.md.compassWrite(self.mid, conf)
    self.assertTrue(self.md.count)

  def test_m(self):
    ''' list model blocksize
    '''
    bsx, bsy = self.md.setBlocksize(mid=15)
    self.assertEqual((3, 2), (bsx, bsy))

  def test_n(self):
    ''' load positions for a model
    '''
    pos = self.md.blocks(mid=15) # model='soleares'
    cell_1_1 = pos[(1, 1)]
    self.assertEqual(cell_1_1[0], 'd')

  def test_o(self):
    ''' can superimposed models list top cells as well?
    '''
    pos = self.md.blocks(mid=15) # soleares
    self.assertEqual(len(pos), 6)
    pos = self.md.blocks(mid=8) # spiral
    self.assertEqual(len(pos), 18)

  def test_p(self):
    ''' key value pair with cells as the key and top as value
    '''
    positions = self.md.blocks(mid=15)
    for p in positions:
      cell, top = positions[p]
      if cell == 'b':
        self.assertFalse(top) # b has no top in soleares

  def test_q(self):
    ''' virtual top 
        cell: g model: marching band
        example of Virtual Top. A cell that exist only as a top cell
    '''
    pos = self.md.blocks(mid=16) # marchingband
    self.pp.pprint(pos)
    cell_g = [pos[p][0] for p in pos if pos[p][0] == 'g']
    self.assertFalse(cell_g)

  def test_r(self):
    ''' superimpose cell d over cell a using top
        pos 1,1 is normally d but with top becomes a
    '''
    pos = self.md.blocks(mid=15) # soleares
    #pp.pprint(pos)
    cells = tuple()
    if type(pos[(2, 0)]) is tuple:
      cells = pos[(2, 0)]
    self.assertEqual(cells[1], 'c')

  def test_s(self):
    ver  = 1 # uniball
    name = self.md.pens(ver)
    self.assertEqual('uniball', name)

'''
the
end
'''
