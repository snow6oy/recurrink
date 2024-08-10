def cmpOnce(doc):
  ''' loop a complex list so that each item 
  is compared to another exactly once
  without ever being compared to itself
  '''
  for g1 in doc:               # first group
    if len(g1['A']):
      a = g1['A'].pop()
      style = g1['B']
      for g2 in doc:           # second group
        if (style != g2['B']): # overlapping is only possible between different groups
          [print(a, b) for b in g2['A']]
      cmpOnce(doc)
doc = [
  { 'A': list('abc'), 'B': 'one' },
  { 'A': list('xyz'), 'B': 'two' }
]
cmpOnce(doc)
