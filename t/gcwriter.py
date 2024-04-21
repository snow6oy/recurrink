import unittest
import pprint
from gcwriter import GcodeWriter
pp = pprint.PrettyPrinter(indent = 2)

class TestLayout(unittest.TestCase):

  def setUp(self):
    self.gcw = GcodeWriter()

  def test_0(self):
    cube = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    self.gcw.writer('/tmp/test_gcwriter.gcode')
    self.gcw.points(cube)
    self.gcw.stop()
    with open('/tmp/test_gcwriter.gcode') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 10)
