'''
transform lower char upper
insert any number
compare transformed versions
'''

def mergeBackground(bgdata, a):
  ''' compare shapes from different layers 
  merge or replace depending on how they overlap
  '''
  for bg in bgdata:
    for i, b in enumerate(bg):
      if a ==  b:
        bg.append(a + b) 
      elif a == '1' and b == 'c':
        bg[i] = 'one'
  return bgdata

def makeFlat(doc):
  ''' loop a nested list so that each item
      from the second list onwards is compared 
      to the first list exactly once
  '''
  bgdata = list()
  [bgdata.append([bg]) for bg in doc.pop(0)]
  for up in doc: # fg and top group
    for cell in up:
      bgdata = mergeBackground(bgdata, cell) 
  return bgdata

doc = [ list('abc'), list('ayzC'), list('bB1') ]
print(doc)
flat_doc = makeFlat(doc)
print('-'*80)
print(flat_doc)

