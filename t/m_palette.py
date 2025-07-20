import unittest
from block import TmpFile
from model import SvgPalette
from pathlib import Path

class Test(unittest.TestCase):

  def test_a(self):
    tf      = TmpFile()
    svgpal  = SvgPalette()
    fn      = 'jeb'
    expect  = Path(f"tmp/{fn}.svg")
    palette = tf.importPalfile(fn)
    svgpal.render(fn, palette)
    self.assertTrue(expect.is_file())

