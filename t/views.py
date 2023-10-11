#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import unittest
from db import Views

import pprint
pp = pprint.PrettyPrinter(indent=2)

class TestViews(unittest.TestCase):

  def setUp(self):
    self.v = Views()
    self.view = 'e4681aa9b7aef66efc6290f320b43e55'

  def testGetViewDigest(self):
    ''' get a view from db as a dictionary
    '''
    view = self.v.read(digest=self.view, celldata=True)
    #pp.pprint(view)
    self.assertEqual(len(list(view.keys())), 4)

  def testGetViewDigestList(self):
    ''' get a view from db as a list
    '''
    view = self.v.read(digest=self.view, celldata=True, output=list())
    # pp.pprint(view[0])
    self.assertEqual(len(list(view[0])), 12)

  def testGetViewMeta(self):
    ''' handle View metadata
    '''
    (model, author, control) = self.v.read(digest=self.view)
    self.assertEqual(author, 'human')

  def testSetView(self):
    ''' no insert will take place because view exists
    '''
    (model, author, control) = self.v.read(digest=self.view)
    self.assertEqual(self.v.create('soleares', self.view, author, control), self.view)

  def testDeleteView(self):
    ''' test delete on a separate view to avoid impacting other tests
    '''
    view = Views()
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
    view.create('koto', 'abcdefghijklmnopqrstuvwxyz012345', 'human', 5)
    self.assertTrue(view.delete('abcdefghijklmnopqrstuvwxyz012345')) 

  def testViewGenerateCompass(self):
    self.v.generate('timpani')
    #pp.pprint(self.v.view)
    self.assertEqual(self.v.view['e']['facing'], 'all')

  def testViewGenerateRandom(self):
    self.v.generate()
    #pp.pprint(self.v.view)
    self.assertTrue(len(self.v.view.keys()))

  def testViewGenerate(self):
    self.v.generate('fourfour') # 'arpeggio'
    #pp.pprint(self.v.view)
    self.assertTrue(isinstance(self.v.view['d'], dict))

  def testColourMap(self):
    d = '1d79457b1dc14203a1eefcf469181072'
    uniq = self.v.colours(d)
    #pp.pprint(uniq)
    #pp.pprint(self.v.colmap)
    n_bg = self.v.colmap[1]
    self.assertEqual(n_bg, ('n', '#DC143C', 'bg'))

  def testCountColour(self):
    digest = [self.view, '0a09ac4a43c8dfa2926f6ba1282906af', '1d79457b1dc14203a1eefcf469181072']
    counts = [2, 3, 12]
    for i, d in enumerate(digest):
      uniq = self.v.colours(d)
      self.assertEqual(counts[i], len(uniq.keys()))
 
  def testStencil(self):
    uniq = self.v.colours(self.view)
    #pp.pprint(self.v.colmap)
    #[print(colour) for colour in list(uniq.keys())]
    self.v.stencil(self.view, '#CCC') # make a stencil for grey only
    pp.pprint(self.v.view)
  ''' 
  the 
  end
  '''
