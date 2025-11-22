import unittest
import pprint
from block import InputValidator
from cell.minkscape import *

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def test_a(self, expect=None, label=None, kind=None, attr=None):
    ''' enum 
    '''
    if self.id() == 't.validator.Test.test_a': # am i myself (:
      expect = 'square'
      label  = 'a'   
      kind   = 'geom'
      attr   = 'name'

    iv    = InputValidator()
    cells = iv.validate(minkscape.cells)
    self.assertEqual(expect, cells[label][kind][attr])

  def test_b(self):
    ''' Color serialised as hex long
    '''
    self.test_a('#009900', 'd', 'color', 'fill')

  def test_c(self):
    ''' Decimal 
    '''
    self.test_a(1.0, 'b', 'stroke', 'opacity')

  def test_d(self):
    ''' stroke is optional
    '''
    iv        = InputValidator()
    no_stroke = minkscape.cells
    del no_stroke['a']['stroke']
    cells = iv.validate(no_stroke)
    self.assertTrue(isinstance(cells, dict)) # return error

  def test_e(self):
    ''' catch invalid input
    '''
    iv        = InputValidator()
    bad_data  = minkscape.cells
    bad_data['a']['stroke']['opacity'] = 'ONE'

    cells     = iv.validate(bad_data)
    self.assertFalse(isinstance(cells, dict)) # return error

'''
the
end
'''
