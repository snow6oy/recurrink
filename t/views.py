#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import unittest
import pprint
from recurrink import Views
#, Models, Cells, Geometry, Styles
pp = pprint.PrettyPrinter(indent=2)

class TestViews(unittest.TestCase):

  def setUp(self):
    self.v = Views()

  def testGetViewDigest(self):
    ''' construct JSON like view from db
    '''
    view = self.v.get(digest='e4681aa9b7aef66efc6290f320b43e55', output='celldata')
    #pp.pprint(view)
    self.assertEqual(len(list(view.keys())), 4)

  def testGetViewModel(self):
    ''' construct JSON like view from db
    '''
    digest, cells = self.v.get(model='soleares')
    # pp.pprint(cells.keys())
    self.assertEqual(len(list(cells.keys())), 4)

  def testViewMeta(self):
    ''' handle View metadata
    '''
    #self.v.write_csvfile('soleares') 
    (model, author) = self.v.get(digest='e4681aa9b7aef66efc6290f320b43e55')
    self.assertEqual(author, 'human')

  def testSetView(self):
    ''' no insert will take place because view exists
    '''
    digest = 'e4681aa9b7aef66efc6290f320b43e55'
    (model, author) = self.v.get(digest=digest )
    control = 3
    self.assertEqual(self.v.set('soleares', digest, author, control), 'e4681aa9b7aef66efc6290f320b43e55')

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
    view.set('koto', 'abcdefghijklmnopqrstuvwxyz012345', 'human', 5)
    self.assertTrue(view.delete('abcdefghijklmnopqrstuvwxyz012345')) 

  def testGetDigest(self):
    digest, _ = self.v.get(model='soleares')
    self.assertEqual(len(digest), 32)
  
  def testViewGenerate(self):
    cells = self.v.generate('soleares')
    # pp.pprint(cells)
    self.assertTrue(cells)

  def testViewGenerateRandom(self):
    ''' pass to avoid spamming styles table
    '''
    pass
    # cells = self.v.generate('soleares', rnd=True)
    # pp.pprint(cells)
    # self.assertTrue(cells)



  ''' the end
  '''
