class Styles:

  def __init__(self, penam=dict()):
    self.fill             = dict()
    self.fill_opacity     = dict()
    self.stroke           = dict()
    self.stroke_dasharray = dict()
    self.stroke_opacity   = dict()
    self.stroke_width     = dict()

    self.fill_penam       = dict()
    self.stroke_penam     = dict()
    self.penam            = penam 

  def add(self, pos, color, stroke=None):
    ''' style.fill[(1,0)] = [
      'brown',  # bg
      'blue',   # fg
      'green'   # top
    ]
        assign values
    '''
    fill  = color['fill']
    self.fill[pos].append(fill)
    self.fill_opacity[pos].append(color['opacity'])

    # fallback to hex unless pen name was defined during init
    if fill in self.penam: self.fill_penam[pos].append(self.penam[fill])
    else: self.fill_penam[pos].append(fill)

    # strokes do not align with YAML where they are a separate object, hmm
    if stroke:
      sfill = stroke['fill']

      if sfill not in self.penam:  # fallback 
        self.penam[sfill] = sfill

      self.stroke[pos].append(sfill)
      self.stroke_penam[pos].append(self.penam[sfill])
      self.stroke_dasharray[pos].append(stroke['dasharray'])
      self.stroke_opacity[pos].append(stroke['opacity'])
      self.stroke_width[pos].append(stroke['width'])
    else:
      self.stroke[pos].append(None)
      self.stroke_dasharray[pos].append(0)
      self.stroke_opacity[pos].append(1)
      self.stroke_width[pos].append(0)
      self.stroke_penam[pos].append(None)

  def addBackground(self, pos, color):
    '''
    if pos not in self.background: self.background[pos] = []
    self.background[pos] = '#' + color['background']
        initialise the attributes we need
    '''
    bgcol = color['background']

    if pos not in self.fill:             self.fill[pos]             = []
    if pos not in self.fill_opacity:     self.fill_opacity[pos]     = []
    if pos not in self.stroke:           self.stroke[pos]           = []
    if pos not in self.stroke_dasharray: self.stroke_dasharray[pos] = []
    if pos not in self.stroke_opacity:   self.stroke_opacity[pos]   = []
    if pos not in self.stroke_width:     self.stroke_width[pos]     = []
    self.fill[pos].append(bgcol)
    self.fill_opacity[pos].append(1)
    self.stroke[pos].append(None)
    self.stroke_dasharray[pos].append(0)
    self.stroke_opacity[pos].append(1)
    self.stroke_width[pos].append(0)

    if pos not in self.fill_penam:   self.fill_penam[pos]   = []
    if pos not in self.stroke_penam: self.stroke_penam[pos] = []

    if bgcol in self.penam: self.fill_penam[pos].append(self.penam[bgcol])
    else: self.fill_penam[pos].append(bgcol)
    self.stroke_penam[pos].append(None)

  def __addPenam(self):
    ''' fake minkscape
    '''
    self.stroke_penam = {
      tuple([0,0]): ['green', 'blue'],
      tuple([1,0]): ['blue'],
      tuple([2,0]): ['blue']
    }
    self.fill_penam   = {
      tuple([0,0]): ['red', 'green', 'blue'],
      tuple([1,0]): ['red', 'blue', 'green'],
      tuple([2,0]): ['red', 'blue']
    }

'''
the
end
'''
