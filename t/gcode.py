import unittest
import pprint
from gcwriter import GcodeWriter
from outfile import Gcode
pp = pprint.PrettyPrinter(indent = 2)

class TestGcode(unittest.TestCase):

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

  def test_1(self):
    ''' ncviewer.com
    '''
    positions = { 
      (0, 0): ('a', 'c'),  # c is both cell and top
      (1, 0): ('b', 'd'),  # d is only top
      (2, 0): ('c',None)
    }
    cells = {
      'a': {
        'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
        'shape': 'square', 'facing': 'all', 'size': 'medium', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      },
      'b': {
        'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
        'shape': 'line', 'facing': 'north', 'size': 'medium', 'top': False,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      },
      'c': {
        'bg': '#CCC', 'fill': '#000', 'fill_opacity': 1.0,
        'shape': 'square', 'facing': 'all', 'size': 'small', 'top': True,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 1.0, 'stroke_width': 0, 
      },
      'd': {
        'bg': '#CCC', 'fill': '#FFF', 'fill_opacity': 1.0,
        'shape': 'line', 'facing': 'east', 'size': 'large', 'top': True,
        'stroke': '#000', 'stroke_dasharray': 0, 'stroke_opacity': 0, 'stroke_width': 0, 
      }
    }
    gc = Gcode(scale=1.0, gridpx=6, cellsize=6)
    gc.gridwalk((3, 1), positions, cells)
    gc.make()
    #pp.pprint(gc.gcdata)
    gc.write('minkscape', fill='fill:#CCC')
    with open('/tmp/minkscape_CCC.gcode') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 85)

'''
the
end
'''
