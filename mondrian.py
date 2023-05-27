#!/usr/bin/env python3

import sys
import getopt
from recurrink import Recurrink

def usage():
  message = '''
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
  r = Recurrink(model, machine=rnd)
  if model:
    if output == 'CSV':                   # create tmp csv file containing a collection of random cell values
      print(r.write_csvfile())            # OR default vals for humans. return cell vals a b c d
    elif view and output == 'RINK':       # write RINK with Library json as source
      r.write_rinkfile(json_file=view)
    elif output == 'RINK':                # write RINK with MODEL.json as source
      r.write_rinkfile()
    elif output == 'JSON':                # convert tmp csv into json as permanent record 
      print(r.write_jsonfile())           # write json and return digest
    elif output == 'CELL':                # get a list of uniq cells
      print(' '.join(r.uniq)) 
    elif cell:                            # lookup values by cell return as comma-separated string '1,square,north'
      print(r.get_cellvalues(cell)) 
    else:
      usage()
  elif ls:
    #print("\n".join(r.list_model()))      # has side effect of setting workdir
    r.list_model_with_stats()               # has side effect of setting workdir
  elif view and output == 'JSON':         # query db
    print(r.find_recurrence(view, 'json')[0])
  elif view and output == 'SVG':          # lookup SVG
    print(r.find_recurrence(view, 'svg')[0])
  else:
    usage()
