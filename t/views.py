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
    #self.r = Recurrink('soleares')
    self.view = 'e4681aa9b7aef66efc6290f320b43e55'
    #550d193efe80f67e92d5a0c59ad9d354'

  def testGetViewDigest(self):
    ''' get a view from db as a dictionary
    '''
    view = self.v.read(digest=self.view, celldata=True)
    # pp.pprint(view)
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

  def testViewGenerate(self):
    cells = self.v.generate('soleares')
    #pp.pprint(cells)
    self.assertTrue(cells)

  def testViewGenerateRandom(self):
    ''' pass to avoid spamming styles table
    '''
    cells = self.v.generate('soleares', rnd=True)
    #pp.pprint(cells)
    self.assertTrue(cells)
  ''' 
  the 
  end
  '''
