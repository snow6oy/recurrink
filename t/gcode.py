import unittest
import pprint
from gcwriter import GcodeWriter
from outfile import Gcode
from flatten import Rectangle
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
    self.gcw.writer('/tmp/gcwriter_t0.gcode')
    self.gcw.points(cube)
    self.gcw.stop()
    with open('/tmp/gcwriter_t0.gcode') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 10)

  def test_1(self):
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
    gc = Gcode(scale=1.0, gridsize=18, cellsize=6)
    gc.gridwalk((3, 1), self.positions, self.data)
    gc.make(uc, cm)

  def test_2(self):
    ''' create a gcode file from a minkscape rink
        by meandering shapes in first pos
        /code/gcode-plotter/ to test visually
    '''
    hw = 90 # height width are same even though A4 = 210x297 mm 
    blocksize = (3, 1)
    gc = Gcode(scale=1, gridsize=hw, cellsize=30)
    self.assertTrue(gc.A4_OK)
    gc.gridwalk(blocksize, self.positions, self.data)
    #pp.pprint(gc.doc)
    for d in gc.doc:   # remove shapes except first position (0, 0)
      del d['shapes'][1:] 
    gc.meanderAll()  
    #pp.pprint(gc.gcdata)
    gc.write('minkscape_t3', fill='fill:#CCC')
    with open(f'/tmp/minkscape_t3_CCC.gcode') as f:
      written = len(f.readlines()) 
    self.assertEqual(written, 72)

  def test_3(self):
    ''' meander all
        create a gcode file from a minkscape rink
        /code/gcode-plotter/ to test visually
    '''
    hw = 90 # height width are same even though A4 = 210x297 mm 
    blocksize = (3, 1)
    gc = Gcode(scale=1, gridsize=hw, cellsize=30)
    self.assertTrue(gc.A4_OK)
    num_of_lines = [224, 644, 716]
    gc.gridwalk(blocksize, self.positions, self.data)
    gc.meanderAll()
    for fill in ['CCC', 'FFF', '000']:
      expected = num_of_lines.pop()
      gc.write('minkscape_t4', fill=f'fill:#{fill}')
      with open(f'/tmp/minkscape_t4_{fill}.gcode') as f:
        written = len(f.readlines()) 
      self.assertEqual(written, expected)

  def test_4(self):
    ''' convert gc.doc shapes into Rectangles()
    '''
    hw = 90 # height width are same even though A4 = 210x297 mm 
    blocksize = (3, 1)
    gc = Gcode(scale=1, gridsize=hw, cellsize=30)
    self.assertTrue(gc.A4_OK)
    gc.gridwalk(blocksize, self.positions, self.data)
    rects = gc.makeRectangles()
    self.assertTrue(isinstance(rects[0][0], Rectangle))

  def test_5(self):
    hw = 90 # height width are same even though A4 = 210x297 mm 
    blocksize = (3, 1)
    gc = Gcode(scale=1, gridsize=hw, cellsize=30)
    self.assertTrue(gc.A4_OK)
    gc.gridwalk(blocksize, self.positions, self.data)
    rects = gc.makeRectangles()
    flattened = gc.makeFlat(rects)
    gc.write4('gcode_t5', flattened, fill='FFF')
'''
the
end
'''
