class Styles:

  def __init__(self):
    self.fill             = dict()
    self.fill_opacity     = dict()
    self.stroke           = dict()
    self.stroke_dasharray = dict()
    self.stroke_opacity   = dict()
    self.stroke_width     = dict()

  def add(self, pos, color, stroke=None):
    ''' style.fill[(1,0)] = [
      'brown',  # bg
      'blue',   # fg
      'green'   # top
    ]
        assign values
    '''
    self.fill[pos].append(color['fill'])
    self.fill_opacity[pos].append(color['opacity'])

    # shall these align with YAML and be a separate object ?
    if stroke:
      self.stroke[pos].append(stroke['fill'])
      self.stroke_dasharray[pos].append(stroke['dasharray'])
      self.stroke_opacity[pos].append(stroke['opacity'])
      self.stroke_width[pos].append(stroke['width'])
    else:
      self.stroke[pos].append(None)
      self.stroke_dasharray[pos].append(0)
      self.stroke_opacity[pos].append(1)
      self.stroke_width[pos].append(0)

  def addBackground(self, pos, color):
    '''
    if pos not in self.background: self.background[pos] = []
    self.background[pos] = '#' + color['background']
        initialise the attributes we need
    '''
    if pos not in self.fill:             self.fill[pos]             = []
    if pos not in self.fill_opacity:     self.fill_opacity[pos]     = []
    if pos not in self.stroke:           self.stroke[pos]           = []
    if pos not in self.stroke_dasharray: self.stroke_dasharray[pos] = []
    if pos not in self.stroke_opacity:   self.stroke_opacity[pos]   = []
    if pos not in self.stroke_width:     self.stroke_width[pos]     = []
    self.fill[pos].append(color['background'])
    self.fill_opacity[pos].append(1)
    self.stroke[pos].append(None)
    self.stroke_dasharray[pos].append(0)
    self.stroke_opacity[pos].append(1)
    self.stroke_width[pos].append(0)
'''
the
end
'''
