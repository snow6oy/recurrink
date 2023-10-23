import unittest
from svgfile import Layout

class TestLayout(unittest.TestCase):

  def setUp(self):
    self.lt = Layout(scale=1.0)

  def testSize(self):
    ''' size is 54 divided by factor 
    '''
    self.assertEqual(self.lt.cellsize, 60)

  def testScale(self):
    l5 = Layout(scale=0.5) # 8 is the 8th scale which is 0.5. size / 0.5 = 108.0
    #print(l5.grid)
    self.assertEqual(l5.grid, 36)

  def testStyle(self):
    bg, fg = self.lt.style('a', {
      'bg':'#FFF',
      'fill':None,
      'fill_opacity':None,
      'stroke':None,
      'stroke_width':None,
      'stroke_dasharray':None,
      'stroke_opacity':None
    })
    self.assertEqual(bg.get('id'), 'a0')
  # TODO
  def testGridWalk(self):
    pass
  def testRenderCell(self):
    pass
  def testRenderBlock(self):
    pass
  '''
  the
  end
  '''
