import unittest
from block import Views
from cell.minkscape import *
import pprint


class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.VERBOSE = False
    self.v       = Views()
    self.digest  = 'e4681aa9b7aef66efc6290f320b43e55'

  def test_a(self):
    ''' get a view from db as a dictionary
    '''
    v1 = self.v.read(digest=self.digest)
    self.assertEqual(len(list(v1.keys())), 4)
    ''' get a view from db as a list
    '''
    v2 = self.v.read(digest=self.digest, output=list())
    #pp.pprint(v2[0]) # cell a has no stroke
    self.assertEqual(len(list(v2[0])), 8)

  def test_b(self):
    ''' handle View metadata
    '''
    (model, author, scale, ver) = self.v.readMeta(digest=self.digest)
    self.assertEqual(author, 'machine')
    self.assertEqual(model, 'soleares')
    self.assertEqual(scale, 1.0)
    self.assertEqual(ver, 3)

  def test_c(self):
    ''' create a view and test that views also makes Cells()
        no insert will take place because view exists
    '''
    celldata = minkscape.cells
    digest = self.v.create(
      self.digest, celldata, model='soleares', author='machine', ver=3
    )
    self.assertEqual(digest, self.digest)

  def test_d(self):
    ''' test delete on a separate view to avoid impacting other tests
    '''
    digest   = 'abcdefghijklmnopqrstuvwxyz012345'
    self.v.create(digest, {}, model='koto', author='human', ver=1)
    self.assertTrue(self.v.delete(digest))

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

  def zz():
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

  ''' 
  the 
  end
  '''
