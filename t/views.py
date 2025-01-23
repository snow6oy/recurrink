#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import unittest
from block import Views

import pprint
pp = pprint.PrettyPrinter(indent=2)

class TestViews(unittest.TestCase):

  def setUp(self):
    self.v = Views()
    self.view = 'e4681aa9b7aef66efc6290f320b43e55'

  def testRead(self):
    ''' get a view from db as a dictionary
    '''
    v1 = self.v.read(digest=self.view)
    #pp.pprint(v1)
    self.assertEqual(len(list(v1.keys())), 4)
    ''' get a view from db as a list
    '''
    v2 = self.v.read(digest=self.view, output=list())
    #pp.pprint(v2[0]) # cell a has no stroke
    self.assertEqual(len(list(v2[0])), 8)

  def testReadMeta(self):
    ''' handle View metadata
    '''
    (model, author, scale, ver) = self.v.readMeta(digest=self.view)
    self.assertEqual(author, 'machine')
    self.assertEqual(model, 'soleares')
    self.assertEqual(scale, 1.0)
    self.assertEqual(ver, 2)

  def testCreate(self):
    ''' test that views also makes Cells()
        no insert will take place because view exists
    '''
    #(model, author, ver) = ('soleares', 'machine', 2)
    celldata = [
      ['a','circle','small','all',False,'#000','#00F',1.0, None, 0, None, None],
      ['b','triangl','medium','north',True,'#FFF','#F00',1.0,'#000',8,1,1.0],
      ['c','square','small','all',True,'#FF0','#FFF',1.0,'#000',8,1,1.0],
      ['d','line','large','south',False,'#000','#FF0',1.0,'#FFF',9,0,1.0]]
    digest = self.v.create(self.view, celldata, model='soleares', author='machine', ver=2)
    self.assertEqual(digest, self.view)

  def testDelete(self):
    ''' test delete on a separate view to avoid impacting other tests
    '''
    view = Views()
    view.create('abcdefghijklmnopqrstuvwxyz012345', [], model='koto', author='human', ver=1)
    self.assertTrue(view.delete('abcdefghijklmnopqrstuvwxyz012345')) 

  def testGenerate(self):
    ''' test a model without compass
    '''

    self.v.generate(1, model='afroclave')  
    #pp.pprint(self.v.view)
    self.assertEqual(len(self.v.view.keys()), 14)

  def testGenerateCompass(self):
    ''' fourfour model has compass defined
        generate_one and generate_all should be called
    '''
    ver = 2
    self.v.generate(ver, model='fourfour') # 'htmstarter') # 'arpeggio'
    #pp.pprint(self.v.view)
    self.assertTrue(self.v.view['a']['facing'], 'all')

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
