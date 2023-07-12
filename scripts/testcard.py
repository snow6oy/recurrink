import json

json_file = '../samples/test_card.json'

def model(name, sz):
  pass

def geometry(g):
  print(g)

with open(json_file) as f:
  test_data = json.load(f)
  model(test_data['id'], test_data['size'])
  for c in test_data['cells']:
    geom = list()
    geom.append(test_data['cells'][c]['shape'])
    geom.append(test_data['cells'][c]['shape_size'])
    geom.append(test_data['cells'][c]['shape_facing'])
    geometry(geom)
