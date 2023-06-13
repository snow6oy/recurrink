class TmpFile():
  ''' read and write data to /tmp
  '''
  def __init__(self):
    self.colnam = ['cell','shape','size','facing','top','fill','bg','fo','stroke','sw','sd','so']
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]


  def write(self, model, keys, celldata):
    with open(f"/tmp/{model}.txt", 'w') as f:
      print(' '.join(self.colnam), file=f)
      for i, data in enumerate(celldata):
        vals = [str(d) for d in data] # convert everything to string
        vals.insert(0, keys[i])
        line = ' '.join(vals)
        print(line, file=f)

  def read(self, model):
    ''' example
        a square medium north False #FFFFFF #CCCCCC 1.0 #000000 0 0 1.0
        return a dictionary keyed by cell
    '''
    sortdata = list()
    cells = dict()
    to_hash = str()

    with open(f"/tmp/{model}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines

    data = [d.split() for d in data[1:]] # ignore header and split on space

    print(data)
    # cell shape size facing top fill bg fill_opacity stroke stroke_width stroke_dasharray stroke_opacity
    # convert values from string to primitives
    for d in data:
      to_hash += ''.join(d)
      d[4] = (d[4] in ['True', 'true'])
      d[9] = int(d[9])
      d[10] = int(d[10])

    # sort them so that top:true will be rendered last
    sortdata = sorted(data, key=lambda x: x[4])

    for d in sortdata:
      z = zip(self.header, d)
      attrs = dict(z)
      cell = attrs['cell']
      del attrs['cell']
      cells.update({cell: attrs})
    return (to_hash, cells)
