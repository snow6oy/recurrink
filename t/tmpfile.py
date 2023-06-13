from recurrink import Views, Blocks
from tmpfile import TmpFile
import unittest
import pprint
import os.path
pp = pprint.PrettyPrinter(indent=2)

class TestTmpFile(unittest.TestCase):

  def setUp(self):
    self.tf = TmpFile()
    self.model = 'soleares'

  def testWrite(self):
    v = Views()
    b = Blocks(self.model)
    celldata = v.generate(self.model, rnd=False) 
    self.tf.write(self.model, b.cells(), celldata)
    self.assertTrue(os.path.isfile('/tmp/soleares.txt'))

  def testRead(self):
    celldata = self.tf.read(self.model)
    pp.pprint(celldata)
