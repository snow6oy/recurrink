#!/usr/bin/env python3

# TODO foreach JSON file in /tmp get digest
# by read json to calc uniq vals and rename file
# update JSON creation to work from mondrian.sh inputs

import csv
import json
from recurrink import Builder


class Mondrian(Builder):
  ''' extend builder to support mondrian 
  '''

  def write_json_file(self, model, fn, data):
    f = f"tmp/{model}/{fn}.json"
    with open(f, "w") as outfile:
      json.dump(data, outfile, indent=2)

  def convert_row2cell(self, data):
    header = [ 'id','output','shape','width','facing','size','bg','top' ]
    source = dict()
    to_hash = str()
    for d in data:
      #z = zip(header, data[i])
      to_hash += ''.join(d)
      z = zip(header, d)
      row = dict(z)
      cell = row['id']
      model = row['output']
      source.update({cell: { 
        'shape': row['shape'],
        'width': int(row['width']),
        'facing':row['facing'],
        'size': row['size'],
        'bg': row['bg'],
        'top': bool(row['top'])
      }})
    return (model, to_hash, source)

  def create_new_instance(self, cell_data):
    ''' example cell data
      a,soleares,triangle,3,west,medium,yellowgreen,False
      b,soleares,circle,8,west,large,orange,True
      c,soleares,line,6,south,medium,gray,True '''
    (model, to_hash, source) = self.convert_row2cell(cell_data)
    # print(model, to_hash)
    self.update_digest(model, to_hash)
    self.write_json_file(model, self.models[model]['id'], source)

  def create_from_log(self, csvfile):
    ''' this function is already obsolete
        but it might be useful to troubleshoot /tmp/model.csv 
    '''
    if csvfile is None:
      csvfile = './mondrian.log'
    with open(csvfile) as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)

    model = None
    counter = 0

    for i, d in enumerate(data):
      if model and model != data[i][1]:
        start = i - counter
        (model, to_hash, source) = self.convert_row2cell(data[start:i])
        print(model, to_hash)
        self.update_digest(model, to_hash)
        self.write_json_file(model, self.models[model]['id'], source)
        counter = 0
      model = data[i][1]
      counter += 1

if __name__ == '__main__':
  m = Mondrian()
  data = [
    [ 'a','test','triangle','3','west','medium','yellowgreen','False' ],
    [ 'b','test','circle','8','west','large','orange','True' ],
    [ 'c','test','line','6','south','medium','gray','True' ]
  ]
  m.create_new_instance(data)

