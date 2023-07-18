import unittest
from svgfile import Layout

class TestLayout(unittest.TestCase):

  def setUp(self):
    l = Layout('soleares', '01')
    self.l = l

  def testCreate(self):
    self.l.create('95')
    self.assertEqual(self.l.factor, 2.0)

  def testScale(self):
    l5 = Layout('soleares', '80') # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
    expected = (108.0, 1080, 1080) # (96.0, 1122.5197, 793.70081)
    self.assertEqual((l5.size, l5.width, l5.height), expected)

  def test_positions(self):
    rs = []
    for y in range(2):
      for x in range(3):
        #print(f"y={y} x={x}")
        rs.append(self.l.get_cell_by_position(tuple([x, y])))
    self.assertEqual(rs, ['a','b','a','c','d','c'])

  def test_sizeUu(self):
    self.assertEqual(self.l.sizeUu, 54.0)
    
  '''
  the
  end
  '''
