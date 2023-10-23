import unittest
from svgfile import Svg

class TestSvg(unittest.TestCase):

  def setUp(self):
    self.svg = Svg(scale=1, cellsize=60)
    self.geometry = {
      'shape':'square',
      'size':'medium',
      'facing':'north',
      'stroke_width': 0
    }

  def testTriangle(self):
    group = self.svg.group(gid='a')
    self.geometry['shape'] = 'triangl'
    self.svg.foreground(x=0, y=0, sid='a1', cell=self.geometry, g=group)
    self.assertTrue(list(self.svg.root.iter(tag=f"{self.svg.ns}polygon")))

  def testDiamond(self):
    ''' are diamonds drawn correctly, excepting formatting differences ?
    '''
    group = self.svg.group(gid='a')
    self.geometry['shape'] = 'diamond'
    self.svg.foreground(x=0, y=0, sid='a1', cell=self.geometry, g=group)
    el = list(self.svg.root.iter(tag=f"{self.svg.ns}polygon"))[0]
    p = el.get("points").split(',')
    points = list(map(float, p))
    self.assertEqual(points, [0.0, 30.0, 30.0, 0.0, 60.0, 30.0, 0.0, 30.0])

  def testBadFacing(self):
    group = self.svg.group(gid='a')
    self.geometry['size'] = 'very tiny'
    with self.assertRaises(ValueError):
      self.svg.foreground(x=0, y=0, sid='a1', cell=self.geometry, g=group)
  '''
  the
  end
  '''
