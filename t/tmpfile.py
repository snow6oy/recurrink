from db import Views, Blocks
from recurrink import TmpFile
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
    celldata = v.create(self.model, rnd=False) 
    self.tf.write(self.model, b.cells(), celldata)
    self.assertTrue(os.path.isfile('/tmp/soleares.txt'))

  def testRead(self):
    celldata = self.tf.read(self.model)
    self.assertEqual(len(celldata.keys()), 4)
    self.assertEqual(len(self.tf.digest), 32)

  def testTopOk2Commit(self):
    ''' check vals from csv are correctly poured, e.g. top reordering
        shape size facing top fill bg fo stroke sw sd so
    '''
    test = [
      [ 'triangle','medium','west','False','#FFF','#FFA500','1.0','#000','1','0','1.0' ],
      [ 'circle','large','all','True','#FFF','#FFA500','1.0','#000','1','0','1.0' ],
      [ 'line','medium','west','False','#FFA500','#CCC','1.0','#000','1','0','1.0' ],
      [ 'circle','large','all','False','#FFF','#FFA500','1.0','#000','1','0','1.0' ]
    ]
    self.tf.write(self.model, ['a','b','c','d'], test)
    cells = self.tf.read(self.model)
    sorted_by_top = list(cells.keys())
    self.assertEqual(sorted_by_top, ['a', 'c', 'd', 'b'])

  def testGetCellValues(self):
    ''' ./recurrink.py -m ${model} --cell ${cell}
    0 1        2      3      4    5    6               7   8    9 0 1   2
    a soleares circle medium west #fff mediumvioletred 1.0 #000 0 0 1.0 True
    '''
    if os.path.isfile('/tmp/soleares.txt'):
      cells = self.tf.read('soleares')
      # pp.pprint(cells['a'])
      self.assertTrue(isinstance(cells['a']['stroke_dasharray'], int))
    else:
      pass

  def testReadText(self):
    soleares_txt = """cell shape size facing top fill bg fo stroke sw sd so
a line medium south False #FFF #32CD32 1.0 #000 0 0 1.5
b square medium all False #FFF #FFA500 1.0 #000 0 0 1.0
c triangle medium east False #FFF #4B0082 1.0 #000 0 0 1.0
d diamond medium south False #CCC #32CD32 1.0 #000 0 0 1.0
"""
    celldata = self.tf.read('soleares', txt=soleares_txt)
    self.assertEqual(len(celldata.keys()), 4)
    self.assertEqual(len(self.tf.digest), 32)
  '''
  the
  end
  '''
