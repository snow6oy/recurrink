import unittest
from block import TmpFile, BlockData
from model import SvgPalette
from pathlib import Path

class Test(unittest.TestCase):

  def test_a(self):
    ''' fetch colors from db and generate html

    palette = tf.importPalfile(fn)
    '''
    bd      = BlockData()
    ver     = 4 
    fn      = 'stabilo68'
    colors  = bd.colors(ver)
    tf      = TmpFile()
    svgpal  = SvgPalette()
    expect  = Path(f"palettes/{fn}.html")
    svgpal.render(fn, colors)
    self.assertTrue(expect.is_file())

