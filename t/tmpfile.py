from block import TmpFile
import unittest
import pprint
import os.path
import random
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.tf = TmpFile()
    self.model = 'minkscape'

  def test_a(self):
    ''' Write soleares.txt in tmp might cause a false positive
    v = Views()
    ver = 1
    model, src, celldata = v.generate(ver, self.model)
    #pp.pprint(celldata)
    celldata = self.tf.convertToList(celldata)
    self.tf.write(self.model, celldata)
    self.assertTrue(os.path.isfile('tmp/soleares.txt'))
    '''

  def test_b(self):
    ''' read the meta stuff'''
    metadata = self.tf.readConf(self.model, meta=True)
    self.assertEqual(3, len(metadata.keys()))

  def test_c(self):
    ''' Read celldata only, no meta stuff '''
    celldata = self.tf.readConf(self.model)
    for label in celldata:
      self.assertTrue(label, 'geom' in celldata[label])

  def test_d(self):
    ''' make digest
    '''
    az = [chr(i) for i in range(97,123,1)]
    r = ''.join(random.choice(az) for i in range(12))
    self.tf.makeDigest(r)
    self.assertEqual(32, len(self.tf.digest))

  def test_d(self):
    ''' check vals from csv are correctly poured, e.g. top reordering
        shape size facing top fill bg fo stroke sw sd so
    test = [
      [ 'a', 'triangl','medium','west','False','#FFF','#FFA500','1.0','#000','1','0','1.0' ],
      [ 'b', 'circle','large','all','True','#FFF','#FFA500','1.0','#000','1','0','1.0' ],
      [ 'c', 'line','medium','west','False','#FFA500','#CCC','1.0','#000','1','0','1.0' ],
      [ 'd', 'circle','large','all','False','#FFF','#FFA500','1.0','#000','1','0','1.0' ]
    ]
    #self.tf.write(self.model, ['a','b','c','d'], test)
    self.tf.write(self.model, test)
    cells = self.tf.read(self.model)
    sorted_by_top = list(cells.keys())
    self.assertEqual(sorted_by_top, ['a', 'c', 'd', 'b'])
    '''

  def test_e(self):
    ''' Get Cell Values
    ./recurrink.py -m ${model} --cell ${cell}
    0 1        2      3      4    5    6               7   8    9 0 1   2
    a soleares circle medium west #fff mediumvioletred 1.0 #000 0 0 1.0 True
    if os.path.isfile('tmp/soleares.txt'):
      cells = self.tf.read('soleares')
      # pp.pprint(cells['a'])
      self.assertTrue(isinstance(cells['a']['shape'], str))
    else:
      raise RuntimeError('missing test dependency')
    '''

  def test_f(self):
    ''' Convert To List 
    celldata = { 
      'a': { 
         'facing': 'south', 
         'shape': 'line', 
         'size': 'medium', 
         'top': False,
         'bg': '#FFA500', 
         'fill': '#FFF', 
         'fill_opacity': 1.0, 
         'stroke_width': 0, 
         'stroke': '#000', 
         'stroke_dasharray': 0, 
         'stroke_opacity': 1.0
      }, 
      'b': {
         'shape': 'circle',
         'size': 'medium',
         'facing': 'all',
         'top':	True,
         'fill': '#32CD32',
         'bg': '#CD5C5C',
         'fill_opacity': 0.4,
         'stroke_width': None, 
         'stroke': None, 
         'stroke_dasharray': None, 
         'stroke_opacity': None
      }
    }
    celllist = self.tf.convertToList(celldata)
    #pp.pprint(celllist)
    self.assertEqual(celllist[0][0], 'a')
    self.assertEqual(celllist[1][8], '') # sw is empty
    '''
'''
the
end
'''

