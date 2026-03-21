import unittest
import pprint
from cell import InputValidator
from cell.minkscape import *

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.iv = InputValidator(ver=99)
    self.defaults = {
      'color': {
        'fill': '#FFF',
        'background': '#CCC',
        'opacity': 1.0,
      }
    }

  def test_a(self):
    ''' validate bad fill fails
    '''
    data                  = self.defaults
    data['color']['fill'] = '#zzzzzz' 
    self.iv.uniqfill      = { '#FFF', '#CCC' }
    #self.iv.validate('a', data)
    self.assertRaises(ValueError, self.iv.validate, 'a', data)

  def test_b(self):
    ''' palette should have opacity greather than 0
    '''
    data = self.defaults
    data['color']['opacity'] = 2
    #[self.assertTrue((o >= 0.1 and o <= 1.0)) for o in self.p.opacity]
    self.assertRaises(ValueError, self.iv.validate, 'a', data)
'''
the
end
'''
