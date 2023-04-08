#!/usr/bin/env python3

# TODO foreach JSON file in /tmp get digest
# by read json to calc uniq vals and rename file
# update JSON creation to work from mondrian.sh inputs

import csv
import json
import random
from recurrink import Builder


class Mondrian(Builder):
  ''' extend builder to support mondrian 
  '''
  def write_tmp_csvfile(self, model):
    with open(f"/tmp/{model}.csv", 'w') as f:
      wr = csv.writer(f, quoting=csv.QUOTE_ALL)
      [wr.writerow(m.random_cellvalues(model, cell)) for cell in self.list_cells(model)]
    return self.list_cells(model)

  def get_cellvalues(self, model, cell):
    data = m.read_tmp_csvfile(model)
    valstr = None
    for d in data:
      if (cell == d[0]):
        valstr = ','.join(d)
        break
    return valstr

  def create_new_instance(self, cell_data):
    ''' convert a 2d array of cell data into a hash and json file
    '''
    (model, to_hash, source) = self.convert_row2cell(cell_data)
    self.update_digest(model, to_hash)
    self.write_json_file(model, self.models[model]['id'], source)
    return self.models[model]['id']

######################### p r i v a t e #############################
  def write_json_file(self, model, fn, data):
    f = f"pub/{model}/{fn}.json"
    with open(f, "w") as outfile:
      json.dump(data, outfile, indent=2)

  def read_tmp_csvfile(self, model):
    with open(f"/tmp/{model}.csv") as f:
      reader = csv.reader(f)
      next(reader, None)
      data = list(reader)
    return data

  def random_cellvalues(self, model, cell):
    # default 'shape':'square',
    shape = random.choice(["circle", "line", "square", "triangle"])
    facing = random.choice(["north", "south", "east", "west"])
    # default 'shape_size':'medium',
    sizes = ["medium", "large"]
    if shape == "triangle":
      size = "medium"
    else:
      size = random.choice(sizes)
    top = str(random.choice([True, False]))
    bg = random.choice(["orange","crimson","indianred","mediumvioletred","indigo","limegreen","yellowgreen","black","white","gray"])
    width = str(random.choice(range(10)))

    return [cell,model,shape,width,facing,size,bg,top]

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

  def create_from_log(self, csvfile):
    ''' this function is already obsolete
        but it might be useful to troubleshoot /tmp/model.csv 
    '''
    data = self.read_tmp_csvfile('./mondrian.log')
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
  ''' three use cases 
    1. create tmp csv file containing a collection of random cell values
    2. lookup values by cell
    3. convert tmp csv into json as permenant record '''
  m = Mondrian()
  data = [
    [ 'a','soleares','triangle','3','west','medium','yellowgreen','False' ],
    [ 'b','soleares','circle','8','west','large','orange','True' ],
    [ 'c','soleares','line','6','south','medium','gray','True' ]
  ]
  print(m.write_tmp_csvfile('soleares'))    # return cell vals a b c d
  print(m.get_cellvalues('soleares', 'b'))  # csv row for cell x
  data = m.read_tmp_csvfile('soleares')
  print(m.create_new_instance(data))        # write json and return digest

