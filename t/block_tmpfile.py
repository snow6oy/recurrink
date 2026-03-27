import unittest
import pprint
import os.path
from block import TmpFile
from cell.minkscape import *
from cell.minkscape_2 import minkscape_2

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.tf = TmpFile()
    self.model = 'minkscape'
    self.paldata = (
      ['#7ac465','0.5','#f37022'],
      ['#7ac465','0.5','#e6aace'],
      ['#7ac465','0.5','#cfe8d3'],
      ['#7ac465','0.5','#fddac4'],
      ['#7ac465','0.5','#8754a1']
    )
    self.metadata = { 
             'id': 'abcdefghijklmnopqrstuvwxyz012345',
          'model':'minkscape', 
        'palette': None, 
      'positions': {
        'foreground': None
      } 
    }

  def test_a(self):
    ''' create seed from minkscape YAML
    '''
    #self.pp.pprint(minkscape.cells)
    seed = self.tf.digestString(minkscape.cells)
    self.assertEqual(144, len(seed))

  def test_b(self):
    ''' make digest
    '''
    self.tf.setDigest(celldata=minkscape.cells)
    self.assertEqual('265550a81314a36daa05b5ed2d81ee1d', self.tf.digest)

  def test_c(self):
    ''' Read celldata only, no meta stuff 
    '''
    if not os.path.isfile(f'conf/{self.model}.yaml'):
      self.test_g()
    celldata = self.tf.readConf(self.model)
    for label in celldata:
      self.assertTrue(label, 'geom' in celldata[label])

  def test_d(self):
    ''' read the meta stuff'''
    if not os.path.isfile(f'conf/{self.model}.yaml'):
      self.test_g()
    metadata = self.tf.readConf(self.model, meta=True)
    self.assertEqual(4, len(metadata.keys()))

  def test_e(self):
    ''' help test_c and test_d 
    '''
    self.tf.writeConf('minkscape', self.metadata, minkscape.cells)
 
  def test_f(self):
    ''' prototype dbv2 write conf in new schema
    '''
    self.tf.writeConf('minkscape_2', self.metadata, minkscape_2.cells)

'''
the 
end
'''
