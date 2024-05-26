class GcodeWriter:

  def __init__(self):
    self.line_num = 1
 
  def writer(self, outfile):
    ''' mecode streams data to serial 
        we do it like this for now 
    '''
    self.f = open(outfile, 'w')

  def custom(self, codes):
    for line in codes:
      self.f.write(f'N{(self.line_num)} ')
      self.f.write(' '.join(line))
      self.f.write("\n")
      if False: # just another way to uncomment
        print(f'N{(self.line_num)}', end=' ')
        [print(code, end=' ', flush=True) for code in line]
        print()
      self.line_num += 1

  def points(self, points):
    ''' pen up, move to start, push pen down then iterate remainder
    '''
    self.pen_up()
    p = points.pop(0)
    self.first_point(p[0], p[1])
    self.pen_down()
    for x, y in points:
      self.f.write(f"N{self.line_num} X{x:.3f} Y{y:.3f}\n")
      #print(f'N{self.line_num} X{x:.3f} Y{y:.3f}')
      self.line_num += 1

  def first_point(self, x, y):
    self.f.write(f"N{self.line_num} G00 X{x:.3f} Y{y:.3f}\n")
    #print(f'N{self.line_num} G00 X{x:.3f} Y{y:.3f}')
    self.line_num += 1
  
  def pen_up(self):
    self.f.write(f"N{self.line_num} G00 Z0.100 ; pen up\n")
    #print(f'N{self.line_num} G00 Z0.100 ; pen up')
    self.line_num += 1

  def pen_down(self):
    self.f.write(f"N{self.line_num} G01 Z-0.030 F3.0 ; pen down\n")
    #print(f'N{self.line_num} G01 Z-0.030 F3.0 ; pen down')
    self.line_num += 1

  def start(self):
    self.custom([
      ('G00','G17','G80'),
      ('G90','G94','G98'),
      ('G54','G43','G21'),  # G21 set to millimetres for NC viewer
      ('T04','H04','M0'),
      ('S1000','M3')
    ])

  def stop(self):
    self.pen_up()
    self.custom([
      ('X0.000','Y0.000'),
      ('M05','M30')
    ])
    self.f.close()

if __name__ == '__main__':
  # test test test
  cell_a = [
    (1, 1), (1, 9), (4, 9), (4, 6), (9, 6), (9, 1), 
    (6, 1), (6, 4), (4, 4), (4, 1), (1, 1)
  ]
  cell_b = [
    (7, 7), (7, 9), (9, 9), (9, 7), (7, 7)
  ]
  gcw = GcodeWriter()
  gcw.writer('/tmp/h.gcode')
  gcw.start()
  gcw.points(cell_a)
  gcw.points(cell_b)
  gcw.stop()

