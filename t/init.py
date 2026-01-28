import unittest
import pprint
from model.data2 import ModelData2
from model.init  import Init

''' generate a YAML from random selection
    apply some controls e.g. pairing based on symmetry
'''

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.VERBOSE = False

  def test_a(self, model=None, pen=None, expect=None, knum=0):
    expect     = expect if expect else ['compass', 'database']
    init       = Init()
    model, pen = init.setInput(model, pen)
    src, data  = init.generate(model=model, pen=pen)
    '''
    print(f'{model=} {pen=}')
    self.pp.pprint(data)
    print(f'{src=} {len(data.keys())=}')
    '''
    self.assertTrue(src in expect)
    if knum: self.assertEqual(knum, len(data.keys()))
    else:    self.assertTrue(len(data.keys()))
    

  def test_b(self):
    ''' fourfour model has compass defined
        generateOne and generateAll should be called
    '''
    self.test_a(model='fourfour', expect='compass', knum=12)

  def test_c(self): self.test_a(pen='staedtler')
  def test_d(self): self.test_a(
    model='waltz', pen='sharpie', expect=['compass'], knum=4
  )
  

''' 
the 
end
'''
