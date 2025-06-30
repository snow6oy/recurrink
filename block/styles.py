class Styles:

  def __init__(self):
    self.fill             = dict()
    self.fill_opacity     = dict()
    self.stroke           = dict()
    self.stroke_dasharray = dict()
    self.stroke_opacity   = dict()
    self.stroke_width     = dict()

  def add(
    self, pos, fill=str(), fill_opacity=1, 
    stroke=None, stroke_opacity=0, stroke_dasharray=0, stroke_width=0
  ):
    ''' style.fill[(1,0)] = [
      'brown',  # bg
      'blue',   # fg
      'green'   # top
    ]

        initialise the attributes we need
    '''
    if pos not in self.fill:             self.fill[pos]             = []
    if pos not in self.fill_opacity:     self.fill_opacity[pos]     = []
    if pos not in self.stroke:           self.stroke[pos]           = []
    if pos not in self.stroke_dasharray: self.stroke_dasharray[pos] = []
    if pos not in self.stroke_opacity:   self.stroke_opacity[pos]   = []
    if pos not in self.stroke_width:     self.stroke_width[pos]     = []

    stroke = stroke if stroke else fill # make a non-stroke invisible

    ''' assign values
    '''

    self.fill[pos].append(fill)
    self.fill_opacity[pos].append(fill_opacity)
    self.stroke[pos].append(stroke)
    self.stroke_dasharray[pos].append(stroke_dasharray)
    self.stroke_opacity[pos].append(stroke_opacity)
    self.stroke_width[pos].append(stroke_width)
