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
    gc.gridwalk(blocksize, self.positions, self.data)
    rects = gc.makeRectangles()
    flattened = gc.makeFlat(rects)
    gc.write4('gcode_t5', flattened, fill='000')
    gc.write4('gcode_t5', flattened, fill='CCC')
    gc.write4('gcode_t5', flattened, fill='FFF')

  def test_6(self):
    hw = 90 # height width are same even though A4 = 210x297 mm 
    blocksize = (3, 1)
    gc = Gcode(scale=1, gridsize=hw, cellsize=30)
    gc.gridwalk(blocksize, self.positions, self.data)
    rects = gc.makeRectangles()
    for layer in rects: # filter out everything except bottom row
      wanted = [0,3,6] if len(layer) == 9 else [0]
      for i, r in enumerate(layer):
        if i in wanted:
          print(f"{(i + 1)} {r.sw.x:>2} {r.sw.y:>2}")
          r.printPoints()
          print()

  def test_7(self):
    ''' merge background with various layers and shapes
    use mock data based on makeRectangles()
    '''
    gc = Gcode(scale=1, gridsize=90, cellsize=30)
    bg = list()
    upper = list()
    for c in [(0,0), (30,0), (60,0)]:
      bg.append(Rectangle(coordinates=c, dimensions=(30,30), pencolor='CCC'))
    d = [(30,30), (10,30), (10,10), (10,10), (50,10)]
    p = ['FFF', '000', '000', '000', 'FFF']
    for i, c in enumerate([(0,0), (40,0), (70,10), (10,10), (20,10)]):
      upper.append(Rectangle(coordinates=c, dimensions=d[i], pencolor=p[i]))
    ''' do the real work here
    '''
    bg = gc.mergeBackground(bg, upper[0])  
    self.assertEqual(bg[0].pencolor, 'FFF') # white instead of grey
    self.assertEqual(len(bg), 3)
    bg = gc.mergeBackground(bg, upper[1])   # ?? black line split grey in 2
    self.assertEqual(len(bg), 5)            # add 3 remove 1
    self.assertEqual(bg[3].pencolor, '000')
    bg = gc.mergeBackground(bg, upper[2])   # small black sq centre
    self.assertEqual(len(bg), 7)            # add 2 gnomons, 1 fg and remove 1 bg
    self.assertEqual(bg[4].direction, 'SE') # only gnomon 
    self.assertEqual(bg[4].pencolor, 'CCC') # 
    self.assertEqual(bg[5].direction, 'NW')
    self.assertEqual(bg[5].pencolor, 'CCC') 
    self.assertEqual(bg[6].pencolor, '000')
    bg = gc.mergeBackground(bg, upper[3])   # small black sq centre
    self.assertEqual(bg[0].pencolor, 'FFF') # white sq became a white gnomon
    self.assertEqual(bg[0].direction, 'SE')
    bg = gc.mergeBackground(bg, upper[4])   # ?? large white line overlays all 3
    self.assertEqual(bg[8].direction, 'N')
    for i, a in enumerate(bg):
      print(i, a.pencolor, a.direction, a.sw.p) 
    print('-' * 80)

'''
the
end
'''
