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
    self.paldata = (
      ['#7ac465','0.5','#f37022'],
      ['#7ac465','0.5','#e6aace'],
      ['#7ac465','0.5','#cfe8d3'],
      ['#7ac465','0.5','#fddac4'],
      ['#7ac465','0.5','#8754a1']
    )

  def test_a(self):
    ''' create seed from minkscape YAML
    '''
    #self.pp.pprint(config.cells)
    seed = self.tf.digestString(config.cells)
    self.assertEqual(144, len(seed))

  def test_b(self):
    ''' make digest
    '''
    self.tf.setDigest(celldata=config.cells)
    self.assertEqual('265550a81314a36daa05b5ed2d81ee1d', self.tf.digest)

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

  def test_e(self):
    self.tf.exportPalfile(self.id(), self.paldata)
    self.assertTrue(os.path.isfile(f'palettes/{self.id()}.txt'))

  def test_f(self):
    ''' run test_e first
    '''
    pal = self.tf.importPalfile('tmpfile_test_e')
    self.assertEqual(5, len(pal))
  

'''
the 
end
'''
