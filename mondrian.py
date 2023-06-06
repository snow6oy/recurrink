#!/usr/bin/env python3

import sys
import random
import getopt
from recurrink import Recurrink, Views

def usage():
  message = '''
-r random model
-l list models
-m MODEL --output CSV  [--random]
-m MODEL --output JSON [--random]
-m MODEL --output RINK [--view VIEW]
-m MODEL --output CELL
-m MODEL --cell CELL
'''
  print(message)

def inputs():
  ''' get inputs from command line
  '''
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "m:o:c:v:lr", ["model=", "output=", "cell=", "view=", "list", "random"])
  except getopt.GetoptError as err:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  (model, output, cell, view, ls, rnd) = (None, None, None, None, False, False)
  for opt, arg in opts:
    if opt in ("-o", "--output") and arg in ('RINK', 'CSV', 'JSON', 'CELL', 'SVG'):
      output = arg
    elif opt in ("-c", "--cell"):
      cell = arg
    elif opt in ("-v", "--view"):
      view = arg
    elif opt in ("-m", "--model"):
      model = arg
    elif opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-l", "--list"):
      ls = True
    elif opt in ("-r", "--random"):
      rnd = True
    else:
      assert False, "unhandled option"
  return (model, output, cell, view, ls, rnd)

if __name__ == '__main__':
  (model, output, cell, view, ls, rnd) = inputs()
  ''''''''''''''''''''''''''''''''''''''''''
  r = Recurrink(model)
  v = Views()
  if model:
    if output == 'CSV':                   # create tmp csv file containing a collection of random cell values
      print(r.write_csvfile(rnd=rnd))     # OR default vals for humans. return cell vals a b c d
    elif view and output == 'RINK':       # write RINK with Library json as source
      r.write_rinkfile(view)
    elif output == 'RINK':                # write RINK with MODEL.json as source
      # r.write_rinkfile()
      print("deprecated")
    elif output == 'JSON':                # convert tmp csv into json as permanent record 
      #(author, view, data) = r.load_view_csvfile(random=rnd)
      #print(r.write_view(view, author, 0, data)) # write json and return digest
      (author, view, cells) = r.load_view_csvfile(random=rnd)
      print(v.set(model, view, author, 0))       # write view metadata and return digest
      [r.write_cell(view, c, list(cells[c].values())) for c in cells]
    elif output == 'CELL':                # get a list of uniq cells
      print(' '.join(r.uniq)) 
    elif cell:                            # lookup values by cell return as comma-separated string '1,square,north'
      print(r.get_cellvalues(cell)) 
    else:
      usage()
  elif ls:
    #print("\n".join(r.list_model()))      # has side effect of setting workdir
    r.list_model_with_stats()               # has side effect of setting workdir
  elif rnd:
    print(random.choice(r.list_model()))
  elif view and output == 'JSON':         # query db
    print(r.find_recurrence(view, 'json')[0])
  elif view and output == 'SVG':          # lookup SVG
    print(r.find_recurrence(view, 'svg')[0])
  else:
    usage()
