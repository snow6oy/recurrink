import unittest
import pprint
from gcwriter import GcodeWriter
from outfile import Gcode
from config import * 
pp = pprint.PrettyPrinter(indent = 2)

class TestGcode(unittest.TestCase):

  def setUp(self):
    self.gcw = GcodeWriter()
    self.positions = config.positions
    self.data = config.cells

  def test_0(self):
    ''' write cube data into a tmpfile
    '''
    cube = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    self.gcw.writer('/tmp/test_gcwriter.gcode')
    self.gcw.points(cube)
    self.gcw.stop()
    with open('/tmp/test_gcwriter.gcode') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 10)

  def test_1(self):
    ''' create a gcode file from a minkscape rink
        /code/gcode-plotter/ to test visually
    '''
    num_of_lines = [92, 260, 239]
    gc = Gcode(scale=1.0, gridpx=18, cellsize=6)
    gc.gridwalk((3, 1), self.positions, self.data)
    gc.make(['fill:#CCC', 'fill:#FFF', 'fill:#000'])
    #pp.pprint(gc.gcdata)
    for fill in ['CCC', 'FFF', '000']:
      expected = num_of_lines.pop()
      gc.write('minkscape', fill=f'fill:#{fill}')
      with open(f'/tmp/minkscape_{fill}.gcode') as f:
        written = len(f.readlines()) 
      self.assertEqual(written, expected)

  def test_2(self):
    ''' stencil yields uniqcol and colmap
        sequence pen up/down and pen col changes
    '''
    uc = ['#FFF', '#000', '#CCC']
    cm = [ ('a', '#FFF', 'fill'),
      ('b', '#000', 'fill'),
      ('b', '#CCC', 'bg'),
      ('c', '#000', 'fill'),
      ('c', '#CCC', 'bg'),
      ('d', '#FFF', 'fill'),
      ('d', '#CCC', 'bg')]
    gc = Gcode(scale=1.0, gridpx=18, cellsize=6)
    gc.gridwalk((3, 1), self.positions, self.data)
    gc.make2(uc, cm)

'''
the
end
'''
