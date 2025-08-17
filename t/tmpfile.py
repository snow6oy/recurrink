import unittest
import pprint
import os.path
from block import TmpFile
from config import *

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.tf = TmpFile()
    self.model = 'minkscape'

  def test_a(self):
    ''' create seed from minkscape YAML
    '''
    #self.pp.pprint(config.cells)
    seed = self.tf.digestString(config.cells)
    self.assertEqual(155, len(seed))

  def test_b(self):
    ''' make digest
    '''
    self.tf.setDigest(celldata=config.cells)
    self.assertEqual('ad2fdea8eac5f642c35d780ba678f8e5', self.tf.digest)

  def test_c(self):
    ''' Read celldata only, no meta stuff '''
    if os.path.isfile(f'conf/{self.model}.yaml'):
      celldata = self.tf.readConf(self.model)
      for label in celldata:
        self.assertTrue(label, 'geom' in celldata[label])

  def test_d(self):
    ''' read the meta stuff'''
    metadata = self.tf.readConf(self.model, meta=True)
    self.assertEqual(3, len(metadata.keys()))

'''
the 
end
'''
