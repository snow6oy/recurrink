shapes = list()

def backgroundCheck(bg, a):
  ''' compare shapes from different layers 
      merge if they overlap
  '''
  [shapes.append(b.upper()) for b in bg if a ==  b]

def cmpOnce(doc):
  ''' loop a nested list so that each item
      from the second list onwards is compared 
      to the first list exactly once
  '''
  [[backgroundCheck(doc[0], cell) for cell in up] for up in doc[1:]] # fg and top group
doc = [ list('abc'), list('ayz'), list('xbz') ]
cmpOnce(doc)
print(shapes)
