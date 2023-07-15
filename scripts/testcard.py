import json
import pprint
from recurrink import TmpFile
pp = pprint.PrettyPrinter(indent=2)

json_file = 'samples/test_card.json'
celldata = list()
positions = list()
block_row = str()
tf = TmpFile()


# 'cell','shape','size','facing','top','fill','bg','fo','stroke','sw','sd','so'
def capitalise(cells):
  for c in cells:
    if ord(c) > 96:  # lower case
      cells[c].insert(0, c)
      #labels[c].insert(0, c.upper())
      print(cells[c])
      #print(labels[c])

with open(json_file) as f:
  test_data = json.load(f)
  bs = tuple(test_data['size'])
  model = test_data['id']
  keys = list(test_data['cells'].keys())
  for c in test_data['cells']:
    data = list()
    data.append(test_data['cells'][c]['shape'])
    data.append(test_data['cells'][c]['shape_size'])
    data.append(test_data['cells'][c]['shape_facing'])
    data.append(False)
    data.append(test_data['cells'][c]['fill'])
    data.append(test_data['cells'][c]['bg'])
    data.append(test_data['cells'][c]['fill_opacity'])
    data.append(test_data['cells'][c]['stroke'])
    data.append(test_data['cells'][c]['stroke_width'])
    data.append(test_data['cells'][c]['stroke_dasharray'])
    data.append(test_data['cells'][c]['stroke_opacity'])
    celldata.append(data)
    for p in test_data['cells'][c]['positions']:
      positions.append([tuple(p), c])
      block_row += f"('{model}', '{{{p[0]}, {p[1]}}}', '{c}'), \n"

#pp.pprint(celldata)
#print(model, keys)
#tf.write(model, keys, celldata)
'''
  ('soleares', '{ 0, 0 }', 'a'),
'''
uniq = len(keys)

print(f"""
INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('{model}', {uniq}, '{{{bs[0]}, {bs[1]}}}', 1.0);"""
)
print(f"""
INSERT INTO blocks (model, position, cell) 
VALUES 
{block_row}"""
)

