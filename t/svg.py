import unittest
from outfile import Svg
from config import *

class TestSvg(unittest.TestCase):

  def setUp(self):
    self.svg = Svg(scale=1, gridpx=180, cellsize=60)
    self.svg.uniqstyle('a', 'fg', False) # create a style so cell 'a' can have a group
    self.group = self.svg.getgroup('fg', 'a')
    self.geometry = {
      'shape':'square',
      'size':'medium',
      'facing':'north',
      'stroke_width': 0
    }
    self.data = config.cells
    self.positions = config.positions

  def test_0(self):
    ''' triangle '''
    self.geometry['shape'] = 'triangl'
    self.svg.foreground(x=0, y=0, cell=self.geometry, g=self.group)
    self.svg.make()
    self.assertTrue(list(self.svg.root.iter(tag=f"{self.svg.ns}polygon")))

  def test_1(self):
    ''' diamond
        are diamonds drawn correctly, excepting formatting differences ?
    '''
    self.geometry['shape'] = 'diamond'
    self.svg.foreground(x=0, y=0, cell=self.geometry, g=self.group)
    self.svg.make()
    el = list(self.svg.root.iter(tag=f"{self.svg.ns}polygon"))[0]
    p = el.get("points").split(',')
    points = list(map(float, p))
    self.assertEqual(points, [0.0, 30.0, 30.0, 0.0, 60.0, 30.0, 0.0, 30.0])

  def test_2(self):
    ''' bad size '''
    self.geometry['size'] = 'very tiny'
    with self.assertRaises(ValueError):
      self.svg.foreground(x=0, y=0, cell=self.geometry, g=self.group)

  def test_3(self):
    #svg = Svg(scale=1.0, gridpx=180) # 180px / 60px = 3 cells high and 3 cells wide
    self.svg.gridwalk((3, 1), self.positions, self.data)
    self.svg.make()
    #pp.pprint(svg.doc)
    self.svg.write('/tmp/minkscape.svg')
    with open('/tmp/minkscape.svg') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 37)

'''
the
end
'''
