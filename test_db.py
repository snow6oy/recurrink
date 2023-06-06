#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import unittest
import pprint
from recurrink import Recurrink, Views
pp = pprint.PrettyPrinter(indent=2)

class TestDb(unittest.TestCase):

  def setUp(self):
    self.db = Recurrink('soleares') # inherit Db() class

  def testListModel(self):
    self.assertTrue('soleares' in self.db.list_model())

  def testLoadModel(self):
    self.assertEqual(self.db.load_model()[1][1], 'd')

  def testSetGeometry(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing combination is new
      also it avoids side-effectof incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.db.set_geometry(['square', 'medium', 'north', False])
    self.assertTrue(int(gid))

  def testSetGeometryTop(self):
    ''' force top to False unless shape is large
      because otherwise when a shared geom is updated there would be side-effects 
      to properly test this first DELETE shape then run test and check top with SELECT
    '''
    gid = self.db.set_geometry(['square', 'medium', 'west', True])
    self.assertTrue(int(gid))

  def testSetGeometryMedium(self):
    ''' only circles, lines and square may be large
      to properly test this first DELETE shape then run test and check top with SELECT
    ''' 
    gid = self.db.set_geometry(['triangle', 'large', 'west', True])
    self.assertTrue(int(gid))

  def testSetStyleUpdate(self):
    ''' styles are not shareable. styles have 1:1 relation view/cell <> style
      this means styles are EITHER updated when the SID exists OR inserted
    '''
    sid = self.db.get_style('e4681aa9b7aef66efc6290f320b43e55', 'd')
    self.assertEqual(sid, 4)
    sid = self.db.set_styles(['#FFF', '#32CD32', 1.0, '#000', 0, 0, 0.5], sid=sid)
    self.assertEqual(sid, 4)

  def testSetStyleInsert(self):
    sid = self.db.set_styles(['#FFF', '#32CD32', 1.0, '#000', 0, 0, 1.5])
    self.assertTrue(sid)

  def testLoadView(self):
    ''' construct JSON like view from db
    '''
    view = self.db.load_view('e4681aa9b7aef66efc6290f320b43e55')
    #pp.pprint(view)
    self.assertEqual(len(list(view.keys())), 4)

  def testWriteView(self):
    v = Views()
    self.db.write_csvfile() 
    (author, view, data) = self.db.load_view_csvfile(view='e4681aa9b7aef66efc6290f320b43e55')
    control = 3
    self.assertEqual(v.set('soleares', view, author, control), 'e4681aa9b7aef66efc6290f320b43e55')

  '''
  def testWriteView(self):
    control = 0
    (author, view, data) = self.r.load_view_csvfile()
    new_view = self.r.write_view(view, author, control, data)
    self.assertEqual(len(new_view), 32)
  '''
  def testDeleteView(self):
    ''' test delete on a separate view to avoid impacting other tests
    '''
    view = Views()
    data = dict()
    cellvals = {
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
    data['c'] = cellvals
    view.set('koto', 'abcdefghijklmnopqrstuvwxyz012345', 'human', 5)
    self.assertTrue(view.delete('abcdefghijklmnopqrstuvwxyz012345')) 

  def testWriteCell(self):
    ''' when mondrian does updsvg and calls ./recurrink.py -c CELL need to run UPDATE on DB
        this is because mondrian -install no longer copies JSON files aroun
    '''
    view = 'e4681aa9b7aef66efc6290f320b43e55'
    cell = 'a'
    data = ['a', 'soleares', 'triangle', 'medium', 'west', '#FFF', '#CCC', 1.0, '#000', 0, 0, 0.5, False]
    self.assertTrue(self.db.write_cell(view, cell, data))

  def testGetDigest(self):
    v = Views()
    self.assertEqual(len(v.get(celldata='abcd')), 32)
  ''' the end
  '''
if __name__ == '__main__':
  unittest.main()
