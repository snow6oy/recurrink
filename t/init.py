import unittest
import pprint
from model.data import ModelData
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
  

#!/usr/bin/env python3

from model.init import Compass
import unittest
import pprint
pp = pprint.PrettyPrinter(indent=2)

class Test(unittest.TestCase):

  def setUp(self):
    self.compass = Compass('timpani')
    data = dict()
    data['c'] = {
      "cell": "c",
      "model": "koto",
      "shape": "diamond",
      "shape_size": "medium",
      "shape_facing": "south",
      "fill": "#FFA500",
      "bg": "#DC143C",
      "fill_opacity": "0.5",
      "stroke": "#DC143C",
      "stroke_width": 0,
      "stroke_dasharray": 0,
      "stroke_opacity": "1",
      "top": False
    }


  def test_a(self):
    ''' lookup recipe for mirroring from model or None
    '''
    pairs, axis = self.compass.one('j')  # j is on the northeast axis
    print(pairs, axis)
    self.assertEqual(pairs[1], 'j')
    self.assertEqual(axis, 'NE')

  def test_b(self):
    ''' lookup recipe for mirroring from model or None
    '''
    self.assertTrue(self.compass.all('k'))

  def test_e(self):
    ''' generate a model without compass
    '''
    self.v.generate(1, model='afroclave')  
    if self.VERBOSE: self.pp.pprint(self.v.view)
    self.assertEqual(len(self.v.view.keys()), 14)

  def test_f(self):
    ''' fourfour model has compass defined
        generate_one and generate_all should be called
    '''
    ver = 2
    self.v.generate(ver, model='fourfour') # 'htmstarter') # 'arpeggio'
    self.assertEqual('C', self.v.view['a']['facing'])

''' 
the 
end
'''
