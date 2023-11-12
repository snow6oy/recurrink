import hmac

class TmpFile():
  ''' read and write data to /tmp
  '''
  def __init__(self):
    self.colnam = ['cell','shape','size','facing','top','fill','bg','fo','stroke','sw','sd','so']
    self.header = [
      'cell','shape','size','facing','top',
      'fill','bg','fill_opacity','stroke','stroke_width','stroke_dasharray','stroke_opacity'
    ]

  def convert_to_list(self, celldata):
    ''' when celldata is in hash format, call this before writing a list 
    '''   
    cells = list()
    for c in celldata:
      cellrow = [c]
      for h in self.header:
        if h == 'cell': # already primed
          continue
        else:
          try: 
            cellrow.append(celldata[c][h])
          except:
            print(f"error missing cell:{c} key:{h}")
      cells.append(cellrow)
    return cells

  def write(self, model, celldata):
    ''' write celldata to a tab separated text file
        data is a list of lists. the inner list must be formatted to match self.header
    '''
    expectedsize = len(self.header)
    givensize = len(celldata[0])
    if givensize != expectedsize:
      raise ValueError(f"{model} celldata has {givensize} not {expectedsize}\n{celldata[0]}")
    with open(f"/tmp/{model}.txt", 'w') as f:
      print("\t".join(self.colnam), file=f)
      for data in celldata:
        vals = [str(d) for d in data] # convert everything to string
        line = "\t".join(vals)
        print(line, file=f)

  def read(self, model, txt=None, output=dict()):
    ''' read text file, convert values from string to primitives and sort on top
        > cell shape size facing top fill bg fo stroke sw sd so
        > a square medium north False #FFF #CCC 1.0 #000 0 0 1.0
        return a dictionary keyed by cell
    '''
    cells = None
    sortdata = list()
    to_hash = str()
    data = self.get_text(txt) if txt else self.get_file(model)

    for d in data:
      to_hash += ''.join(d)
      d[4] = (d[4] in ['True', 'true'])
      d[9] = int(d[9])
      d[10] = int(d[10])
    self.set(to_hash)
    # sort them so that top:true will be rendered last
    sortdata = sorted(data, key=lambda x: x[4])

    if isinstance(output, list):
      cells = sortdata 
    elif isinstance(output, dict):
      cells = dict()
      for d in sortdata:
        z = zip(self.header, d)
        attrs = dict(z)
        cell = attrs['cell']
        del attrs['cell']
        cells.update({cell: attrs})
    else:
      raise TypeError(f"unsupported type {output}")
    if not cells: # is model with given name available from db ?
      raise ValueError(f'non readable <{model}>')
    return cells

  def get_file(self, model):
    with open(f"/tmp/{model}.txt") as f:
      data = [line.rstrip() for line in f] # read and strip newlines
    data = [d.split() for d in data[1:]] # ignore header and split on space
    return data

  def get_text(self, text):
    data = list()
    [data.append(line.split()) for line in text.splitlines()]
    del data[0] # remove header
    return data

  def set(self, key):
    ''' make a digest that has a unique value for each model view
    '''
    secret = b'recurrink'
    digest_maker = hmac.new(secret, key.encode('utf-8'), digestmod='MD5')
    self.digest = digest_maker.hexdigest()
