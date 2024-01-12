import os.path
import re
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
        # not needed because read will convert empties correctly
        if h in ['stroke', 'stroke_width', 'stroke_dasharray', 'stroke_opacity']:
          if celldata[c][h] is None:
            celldata[c][h] = str() # TODO remove or delete to empty a dictionary entry?
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
    if len(celldata) == 0:
      raise ValueError(f"{model} celldata is empty")
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
      if len(d) > 8: # has stroke entries
        d[9] = int(d[9])
        d[10] = int(d[10])
      else:
        d += [None, 0, None, None]
    self.set(to_hash) # make digest
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

  def conf(self, model=None, ver=None):
    '''reads all symlinks
       when there is exactly one, continue but 0 or > 1 throw error

       when given a ver and a model
       removes old link and create new
       else read and return
    '''
    links = self.tmplinks()
    if len(links) == 1:
      link = links[0]
      path = f'/tmp/{link}'
      if model and ver: # swap old and new
        os.unlink(path)
        os.symlink(f'/tmp/{model}.txt', f'/tmp/{ver}')
        return None
      else: # read link
        path = os.readlink(path)
        model = re.findall(r"[a-z0-9]+", path)[1]
        return model, link
    elif len(links) == 0 and model and ver: # first time
      os.symlink(f'/tmp/{model}.txt', f'/tmp/{ver}')
    else:
      raise ValueError(f'unexpected number of links {len(links)}')

  def tmplinks(self):
    links = list()
    for _, _, files in os.walk('/tmp/'):
      for f in files:
        if os.path.islink(f'/tmp/{f}'):
          links.append(f)
    return links
