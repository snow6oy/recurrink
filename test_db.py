#!/usr/bin/env python3

''' see recurrink-ddl and recurrink-dml sql
'''
import unittest
import pprint
from recurrink import Recurrink
pp = pprint.PrettyPrinter(indent=2)

class TestDb(unittest.TestCase):

  def setUp(self):
    self.db = Recurrink('soleares')

  def testListModel(self):
    self.assertTrue('soleares' in self.db.list_model())

  def testLoadModel(self):
    self.assertEqual(self.db.load_model()[1][1], 'd')

  def testLoadView(self):
    ''' construct JSON like view from db
    '''
    view = self.db.load_view('e4681aa9b7aef66efc6290f320b43e55')
    #pp.pprint(view)
    self.assertEqual(len(list(view.keys())), 4)

  def testSetGeometry(self):
    ''' geometries are shared and have a 1:* relation with views and cells
      geometries are never updated, only inserted when shape/size/facing combination is new
      also it avoids side-effectof incrementing SERIAL by anticipating UniqueViolation '''
    gid = self.db.set_geometry(['square', 'medium', 'north', False])
    self.assertEqual(gid, 3)

  def testSetGeometryTop(self):
    ''' force top to False unless shape is large
      because otherwise when a shared geom is updated there would be side-effects 
      to properly test this first DELETE shape then run test and check top with SELECT
    '''
    gid = self.db.set_geometry(['square', 'medium', 'west', True])
    self.assertTrue(gid)

  def testSetGeometryMedium(self):
    ''' only circles, lines and square may be large
      to properly test this first DELETE shape then run test and check top with SELECT
    ''' 
    gid = self.db.set_geometry(['triangle', 'large', 'west', True])
    self.assertTrue(gid)

  def testSetStyleUpdate(self):
    ''' styles are not shareable. styles have 1:1 relation view/cell <> style
      this means styles are EITHER updated when the SID exists OR inserted
    '''
    sid = self.db.get_style('e4681aa9b7aef66efc6290f320b43e55', 'd')
    self.assertEqual(sid, 4)
    sid = self.db.set_styles(['#fff', 'limegreen', 1.0, '#000', 0, 0, 0.5], sid=sid)
    self.assertEqual(sid, 4)

  def testSetStyleInsert(self):
    sid = self.db.set_styles(['#00f', 'limegreen', 1.0, '#000', 0, 0, 1.5])
    self.assertTrue(sid)

  def testWriteCell(self):
    view = 'e4681aa9b7aef66efc6290f320b43e55'
    cell = 'a'
    author = 'machine'
    data = ['a', 'soleares', 'triangle', 'large', 'west', '#fff', 'limegreen', 1.0, '#000', 0, 0, 0.5, True]
    self.assertTrue(self.db.write_cell(view, cell, author, data))

  def testWriteView(self):
    #print(self.db.write_jsonfile())
    pass

  def testUpdateView(self):
    ''' when mondrian does updsvg and calls ./recurrink.py -c CELL need to run UPDATE on DB
      this is because mondrian -install no longer copies JSON files aroun
    '''
    # print(db.write_jsonfile(view='e4681aa9b7aef66efc6290f320b43e55', author='machine'))
    pass

if __name__ == '__main__':
  unittest.main()
