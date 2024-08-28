'''
transform lower char upper
insert any number
compare transformed versions
'''

def newCell(a, b, bg):
  ''' decide how two shapes overlap
  merge or replace depending on how they overlap
  return an amended list of shapes
  '''
  if b == 'a':
    bg = [b.upper()]
  elif b == 'b': 
    bg = [a, b]  # remain visible
  return bg 

def transformBackgroundCells(bgdata, a):
  ''' loop through background cells
  return a nested list of cells and shapes
  '''
  tx = list() 
  [[tx.append(newCell(a, b, bg)) for b in bg] for bg in bgdata]
  return tx

###############################################################################
def newCell2(a, b):
  ''' as above but returns empty list when not found
  '''
  bg = list()
  if b == 'a':
    bg = [b.upper()]
  elif b == 'b': 
    bg = [a, b] # remain visible
  elif b == 'x': # second pass
    bg = [b + a]
  return bg 

def transformBackgroundCells2(bgdata, a):
  ''' loop through background cells
  return a nested list of cells and shapes
  '''
  tx = list() 
  for bg in bgdata:
    for b in bg:
      cell = newCell2(a, b)
      if len(cell):
        break
    else:
      tx.append(bg) # nothing found, restore what was alread there
      continue
    tx.append(cell) # new cell replaces old background
  return tx

def flatten(doc):
  ''' loop a nested list so that each item
      from the second list onwards is compared 
      to the first list exactly once
  '''
  bgdata = list()
  [bgdata.append([bg]) for bg in doc.pop(0)]
  #print(bgdata)
  for up in doc: # fg and top group
    for cell in up:
      #bgdata = transformBackgroundCells(bgdata, cell) 
      bgdata = transformBackgroundCells2(bgdata, cell) 
  return bgdata

doc = [ list('abc'), list('xy') ]
#print(doc)
flat_doc = flatten(doc)
print(flat_doc) 
