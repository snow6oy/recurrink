'''
transform lower char upper
insert any number
compare transformed versions
'''
def newCell2(lo, up):
  ''' as above but returns empty list when not found
  '''
  bg = list()
  hidden = False
  print(lo, up)
  if lo == 'a' and up == 'x':   # transform
    bg = [lo.upper()]
  elif lo == 'b' and up == 'y': # transform and merge
    bg = [lo.upper(), up] 
  elif lo == 'A':            # combine on second pass
    hidden = True
    bg = [lo + up]
  return hidden, bg 

def transformBackgroundCells2(bgdata, up):
  ''' loop through background cells
  return a nested list of cells and shapes
  '''
  tx = list() 
  for bg in bgdata:
    for lo in bg:
      hidden, shapes = newCell2(lo, up)
      if len(shapes):
        break
    else:
      tx.append(bg) # nothing found, restore what was alread there
      continue
    if hidden:
      tx.append(shapes) # replace new with old
    else:
      bg.extend(shapes) # merge new and old
      tx.append(bg) 
  return tx
###############################################################################
def newCell(a, b, bg):
  ''' decide how two shapes overlap
  merge or replace depending on how they overlap
  return an amended list of shapes
  '''
  if a == 'x':
    bg = [b.upper()]
  elif a == 'y': 
    bg = [a, b]  # remain visible
  return bg 

def transformBackgroundCells(bgdata, a):
  ''' loop through background cells
  return a nested list of cells and shapes
  '''
  tx = list() 
  [[tx.append(newCell(a, b, bg)) for b in bg] for bg in bgdata]
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
print(doc)
flat_doc = flatten(doc)
print(flat_doc) 
