import os
import datetime 
import pprint
from cell import Commit as CellCommit
from config import *
from .palette import PaletteMaker
from .tmpfile import TmpFile
from .data import BlockData
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Commit(BlockData):
  ''' read config, write to database and return digest
  '''
  pp      = pprint.PrettyPrinter(indent=2)
  pmk     = PaletteMaker()
  tf      = TmpFile()
  #tx      = Transform()
  cc      = CellCommit()
  WORKDIR = config.directory['rinks']
  PUBDIR  = config.directory['pubq']
  PALDIR  = config.directory['palettes']

  def addColor(self, ver, penam):
    ''' pass new pen set to BlockData.colours
    '''
    gpldata = self.pmk.readInkscapePal(self.PALDIR, f'{penam}.gpl')
    self.colors(ver, colors=gpldata)
    return self.count

  def addRink(self, mid, model, size, factor, pens):
    ''' do the real work here
    '''
    metadata = self.tf.readConf(model, meta=True)
    if metadata['id']:
      raise TypeError(f"""found {metadata['id']} in conf
not adding to database in case it causes duplication
setting >id: null< in {model}.yaml avoids this message""")

    if metadata['palette'] in pens:
      ver   = pens.index(metadata['palette'])
      penam = metadata['palette']
    else:
      ver   = 0
      penam = None
    celldata = self.tf.readConf(model)
    rinkid = self.tf.setDigest(celldata=celldata)
    #print(rinkid, mid, ver, size, factor)
    if os.path.isdir(f"{self.WORKDIR}/{model}"):
      self.rinks(rinkid, [mid, ver, size, factor]) # write new to DB
      if self.count:
        celldata = self.cc.dataV2(celldata)  # TODO should use dataV3 ?
        self.layers(rinkid, celldata=celldata)
        # TODO self.moveTmpfile(model, rinkid)
      else:
        raise ValueError('db error adding rink')
    else:
      raise FileNotFoundError(f"{model} not found in {self.WORKDIR}")
    return rinkid, ver, penam

  def updateVer(self, model, pens):
    ''' read and write back same, except ver
    '''
    metadata = self.tf.readConf(model, meta=True)
    if metadata['id']:
      rinkid = metadata['id']
      penam  = metadata['palette']
      ver    = pens.index(penam)
    else:
      raise ValueError(f'{model}.yaml has no conf.id. stopping palswap')
    mid, _, size, factor, created, pubdate = self.rinks(rinkid)
    self.rinks(rinkid, [mid, ver, size, factor, created, pubdate])
    return self.count, penam

  def updatePubdate(self, rinkid): 
    # TODO rinksUpdate has to accept pubdate as well as ver
    ''' was used by reith but now it represents plotdate
        e.g. 2024-01-27 22:26:12
    '''
    rinkdata = self.rinks(rinkid)
    if len(rinkdata) == 6:
      mid, ver, size, factor, created, pubdate = rinkdata
      pubdate = '{d:%Y-%m-%d %H:%M:%S}'.format(d=datetime.datetime.now())
      self.rinks(rinkid, [mid, ver, size, factor, created, pubdate])
      out = f'''
pubdate: {pubdate}
rows impacted: {self.count}'''
    else:
      out = f'{rinkid} not returned by db'
    return out

  def remove(self, rinkid):
    ''' remove is tricky because of db deps
    '''
    rinkdata = self.rinks(rinkid) 
    if rinkdata:
      out = self.rinksDelete(rinkid)
      mid = rinkdata[0]
    else: 
      raise ValueError(f'nothing named {rinkid} in database')
    return mid, out

  def moveTmpfile(model, rinkid):
    ''' unused
    '''   
    if os.path.isfile(f"tmp/{model}.svg"):
      svgname = f"{WORKDIR}/{model}/{rinkid}.svg"
      os.rename(f"tmp/{model}.svg", svgname)
      os.symlink(f"{svgname}", f"{PUBDIR}/{rinkid}.svg")
      return svgname
    else:
      raise FileNotFoundError(f"{model}.svg not found in tmp")

  def removeSvg(model, rinkid):
    ''' also unused 
    '''
    if os.path.isfile(f'{PUBDIR}/{rinkid}.svg'):
      os.unlink(f'{PUBDIR}/{rinkid}.svg')
    if os.path.isfile(f'{WORKDIR}/{model}/{rinkid}.svg'):
      os.unlink(f'{WORKDIR}/{model}/{rinkid}.svg')
      return f'{rinkid} deleted ok' # success
    else: 
      raise FileNotFoundError(f'SVG not deleted {model}/{rinkid}')
'''
the
end
'''
