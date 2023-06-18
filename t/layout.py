import unittest
from svgfile import Layout

class TestLayout(unittest.TestCase):

  def setUp(self):
    l = Layout('soleares')
    self.l = l
  
  def test_scale(self):
    l5 = Layout('soleares', factor=0.5)
    self.assertEqual((l5.size, l5.width, l5.height), (96.0, 1122.5197, 793.70081))

  def test_positions(self):
    rs = []
    for y in range(2):
      for x in range(3):
        #print(f"y={y} x={x}")
        rs.append(self.l.get_cell_by_position(tuple([x, y])))
    self.assertEqual(rs, ['a','b','a','c','d','c'])

  def test_sizeUu(self):
    self.assertEqual(self.l.sizeUu, 48.0)
  '''
    the end
  '''
