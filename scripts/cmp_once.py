'''
transform lower char upper
insert any number
compare transformed versions
'''

def mergeBackground(bg, a):
  ''' compare shapes from different layers 
      merge if they overlap
  '''
  found = None
  for i, b in enumerate(bg):
    if a ==  b:
      bg[i] = b.upper() 
    elif a == '1':
      found = 'one'
  # better to concatenate two lists
  bg.append(found) if found else None
  return bg

def makeFlat(doc):
  ''' loop a nested list so that each item
      from the second list onwards is compared 
      to the first list exactly once
  '''
  bg = doc.pop(0)
  for up in doc: # fg and top group
    for cell in up:
      bg = mergeBackground(bg, cell) 
  return bg

doc = [ list('abc'), list('ayzC'), list('bB1') ]
flat_doc = makeFlat(doc)
print(doc)
print(flat_doc)

