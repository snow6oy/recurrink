from db import Db
class Styles(Db):

  def __init__(self):
    super().__init__()
    self.fill = {
      'orange':'#FFA500',
      'crimson':'#DC143C',
      'indianred':'#CD5C5C',
      'mediumvioletred':'#C71585',
      'indigo':'#4B0082',
      'limegreen':'#32CD32',
      'yellowgreen':'#9ACD32',
      'black':'#000',
      'white':'#FFF',
      'gray':'#CCC',
      '#fff':'#FFF',
      '#ccc':'#CCC',
      '#333':'#CCC'
    }
    self.defaults = {
      'fill': '#FFF',
      'bg': '#CCC',
      'fill_opacity':1.0,
      'stroke':'#000',
      'stroke_width': 0,
      'stroke_dasharray': 0,
      'stroke_opacity':1.0
    }
    self.colours = ['#FFF','#CCC','#CD5C5C','#000','#FFA500','#DC143C','#C71585','#4B0082','#32CD32','#9ACD32']
    self.opacity = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1 ] 
    self.strokes = [n for n in range(1, 11)]

  def validate(self, items):
    ''' old bad code has various ways of saying RED BLUE GREEN
    '''
    for f in self.fill:
      items[0] = items[0].replace(f, self.fill[f])
      items[1] = items[1].replace(f, self.fill[f])
      items[3] = items[3].replace(f, self.fill[f])
    return items

  def set(self, items=[], sid=None):
    ''' update with sid or insert or randomly create
        always returns a list
    '''
    if sid:
      #print(len(items),sid)  
      items.append(sid)
      self.cursor.execute("""
UPDATE styles SET
fill=%s, bg=%s, fill_opacity=%s, stroke=%s, stroke_width=%s, stroke_dasharray=%s, stroke_opacity=%s
WHERE sid=%s;""", items)
      sid = tuple([sid])  # repackage for consistency
    elif items:
      sid = self.add(items)
    else: # quick make something up!
      items = []
      items.append(random.choice(self.colours))  # fill
      items.append(random.choice(self.colours))  # bg
      items.append(random.choice(self.opacity))  # fill_opacity
      items.append(random.choice(self.colours))  # stroke
      items.append(random.choice(self.strokes))  # width
      items.append(random.choice(self.strokes))  # dash
      items.append(random.choice(self.opacity))  # stroke_opacity
      sid = self.add(items)  # no check for duplication, testing will spam the styles table :/
    return sid + tuple(items)

  def get(self, view=None, cell=None, rnd=False, sid=None):
    ''' select various items according to incoming params
        always return a list
    '''
    styles = list()
    if sid:
      self.cursor.execute("""
SELECT fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity
FROM styles
WHERE sid = %s;""", [sid])
      styles = self.cursor.fetchone()
    elif rnd:
      self.cursor.execute("""
SELECT MAX(sid)
FROM styles;""", [])
      maxsid = self.cursor.fetchone()[0]
      sids = list()
      [sids.append(i) for i in range(1, maxsid + 1)]
      styles = self.get(sid=random.choice(sids))
    elif view and cell:
      self.cursor.execute("""
SELECT sid
FROM cells
WHERE view = %s
AND cell = %s;""", [view, cell])
      styles = self.cursor.fetchone()
    else:
      pass # raise error here?
    return styles

  def add(self, items):
    ''' private method called by self.set()
        returns tuple with single elem
    '''
    items = self.validate(items)
    self.cursor.execute("""
INSERT INTO styles (sid, fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
RETURNING sid;""", items)
    sid = self.cursor.fetchone()
    return sid

  def update(self, cells, control):
    if control == 1:
      for c in cells:
        cells[c]['stroke_width'] = 0
    return cells
