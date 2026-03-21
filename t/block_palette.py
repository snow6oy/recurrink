import os.path
import unittest
import pprint
from block import PaletteMaker, TmpFile
from config import *

class Test(unittest.TestCase):

  def setUp(self):
    self.pmk = PaletteMaker()
    self.pp  = pprint.PrettyPrinter(indent=2)

  def test_a(self):
    ''' read inkscape gpl file
    '''
    pal_dir = config.directory['palettes'] 
    gpldata = self.pmk.readInkscapePal(pal_dir, 'uniball.gpl')
    self.assertEqual(8, len(gpldata))

  def test_b(self):
    ''' add new colours from txt to db

        first run ./recurrink init -p8
        get pal from tf.importPalfile 
        filter through block.palette.makeUnique()
        and update db
    '''
    ver    = 8
    txtpal = [
      ['#d40000', '0.5', '#dd55ff'],
      ['#0055d4', '0.5', '#4400aa'],   # dup
      ['#d40000', '0.5', '#4400aa'],
      ['#ffffff', '0.5', '#000000']
    ]
    dbpal  = [                         # slice of uniball pal
      ('#0055d4', 0.5, '#00ffff'),
      ('#0055d4', 0.5, '#4400aa'),     # dup
      ('#0055d4', 0.5, '#2a7fff'),
      ('#0055d4', 0.5, '#d40000')
    ]
    new_pal = self.pmk.makeUnique(ver, dbpal, txtpal)
    self.assertEqual(3, len(new_pal))

  def test_c(self):
    ''' do complimentary relations exist ?
    #dc143c crimson 
    #c71585 mediumvioletred 
    #ffa500 orange 
    #32cd32 limegreen 
    #4b0082 indigo
    '''
    expected = {
      '#dc143c': '#14dcb4', 
      '#c71585': '#15c756',
      '#ffa500': '#005aff',
      '#32cd32': '#cd32cd',
      '#4b0082': '#378200',
      '#ff0000': '#00ffff',
      '#ffff00': '#0000ff',
      '#0000ff': '#fffe00',
      '#ffffff': '#ffffff',
      '#000000': '#000000'
    }
    [self.assertEqual(expected[f], self.pmk.secondary(f)) 
       for f in ['#dc143c', '#c71585', '#ffa500' ,'#32cd32', '#4b0082']
    ]
    [self.assertEqual(expected[f], self.pmk.secondary(f)) 
       for f in ['#ff0000', '#ffff00', '#0000ff' ,'#ffffff', '#000000']
    ]

'''
the 
end
'''
