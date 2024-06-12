#!/usr/bin/env python3
import pprint
import filecmp
import unittest
from views import Views, Models, Blocks
from outfile import Svg
from tmpfile import TmpFile
pp = pprint.PrettyPrinter(indent=2)
class TestE2E(unittest.TestCase):
  ''' test to check the end to end life cycle of a rink
      cd recurrink
      python3 -m unittest t.e2e
  '''
  def setUp(self):
    self.digest = 'e4681aa9b7aef66efc6290f320b43e55',
  def test_1(self): 
    ''' init -v DIGEST
    '''
    v = Views()
    celldata = v.read(digest=self.digest, output=list())
    #pp.pprint(celldata)
    model, author, scale, ver = v.read_meta(digest=self.digest)
    #print(model, author, scale, ver)
    self.assertTrue(scale)
    tf = TmpFile()
    tf.write(model, celldata)
    ok = filecmp.cmp(f'/tmp/{model}.txt', f't/{model}.txt')
    self.assertTrue(ok)
  def test_2(self):
    ''' update -m MODEL
    '''
    v = Views()
    m = Models()
    tf = TmpFile()
    model, author, scale, ver = v.read_meta(digest=self.digest)
    #b = Blocks(model)
    blocksize = m.read(model=model)[2] # can get scale too
    #positions = b.read()
    positions = m.read_positions(model)
    svg = Svg(scale=scale)
    #print(f"s {svg.scale} c {svg.cellsize} g {svg.grid}")
    #print(type(svg.scale))
    self.assertTrue(scale)
    self.assertEqual(svg.cellsize, 60)
    self.assertEqual(svg.grid, 18)
    cells = tf.read(model, output=dict())
    v.validate(cells, ver=ver)
    svg.gridwalk(blocksize, positions, cells)
    svg.make()
    svg.write(f'/tmp/{model}.svg')
    ok = filecmp.cmp(f'/tmp/{model}.svg', f't/{model}.svg')
    self.assertTrue(ok)
  def test_3(self):
    ''' delete -v DIGEST
    '''
    v = Views()
    v.delete(self.digest) 
    data = v.read_celldata(self.digest)
    self.assertFalse(data)
  def test_4(self):
    ''' commit and force digest to be the same for next time
    '''
    v = Views()
    tf = TmpFile()
    model, author, scale, ver = ('soleares', 'machine', 1, 2)
    celldata = tf.read(model, output=list())
    #pp.pprint(celldata[0])
    self.assertEqual(len(celldata), 4)
    v.create(self.digest, celldata, model=model, author=author, ver=ver)
# in case recovery from /tmp fails hard-code here instead
txt = """cell shape size facing top fill bg fo stroke sw sd so
a       circle  small   all     False   #000    #00F    1.0
b       triangl medium  north   True    #FFF    #F00    1.0     #000    8       1       1.0
c       square  small   all     True    #FF0    #FFF    1.0     #000    8       1       1.0
d       line    large   south   False   #000    #FF0    1.0     #FFF    9       0       1.0
"""
#cellhash = tf.read(model, txt=txt)
#pp.pprint(cellhash['a'])
#celldata = tf.convert_to_list(cellhash)
