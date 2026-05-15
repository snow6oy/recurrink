''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import os
import datetime 
import pprint
from block import Commit as BlockCommit
from config import *
from .data import ModelData
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Commit(ModelData):
  ''' read config, write to database and return digest
  '''
  pp      = pprint.PrettyPrinter(indent=2)
  bc      = BlockCommit()
  WORKDIR = config.directory['rinks']
  PLOTDIR  = config.directory['plotq']
  PALDIR  = config.directory['palettes']

  def addColor(self, penam):
    ''' create new color entries
        entry in pens table should be made manually before
    '''
    pens = self.pens()
    if penam in pens:
      ver = pens.index(penam)
      num = self.bc.addColor(ver, penam)
      return f'{num} colors added'
    else:
      return f'{penam} does not exist. add to pens table and try again'

  def addRink(self, model, size, factor):
    ''' pass model data to block where the rink will be added
    '''
    mid      = self.model(name=model)
    pens     = self.pens()

    rinkid, ver, penam = self.bc.addRink(mid, model, size, factor, pens)
    # only reach this point if conf.id was null
    if os.path.isfile(f'conf/{model}.yaml'): # commit is idempotent
      os.unlink(f'conf/{model}.yaml')
    # TODO self.moveTmpfile(model, rinkid)
    return f'''
created {rinkid}
{model} {mid=}
{penam} {ver=}
{size=} {factor=}

{model}/{rinkid}.svg
was NOT copied to {self.WORKDIR}

removed {model}.yaml from conf'''

  def updateVer(self, model):
    ''' taking new ver from conf transformed by clone
    '''
    pens       = self.pens()
    num, penam = self.bc.updateVer(model, pens)
    return f'''
new palette: {penam}
rows impacted: {num}'''

  def updatePubdate(self, rinkid): 
    # TODO rinksUpdate has to accept pubdate as well as ver
    ''' was used by reith but now it represents plotdate
        e.g. 2024-01-27 22:26:12
    '''
    return self.bc.updatePubdate(rinkid)

  def remove(self, rinkid):
    ''' remove is tricky because of db deps
    '''
    mid, out = self.bc.remove(rinkid)
    # no exception from BlockCommit .. continue
    model = self.model(mid=mid)
    print(f'not removing SVG {model}/{rinkid}')
    # out  += self.removeSvg(model, rinkid)
    return out

  def moveTmpfile(model, rinkid):
    ''' unused
    '''   
    if os.path.isfile(f"tmp/{model}.svg"):
      svgname = f"{WORKDIR}/{model}/{rinkid}.svg"
      os.rename(f"tmp/{model}.svg", svgname)
      os.symlink(f"{svgname}", f"{PLOTDIR}/{rinkid}.svg")
      return svgname
    else:
      raise FileNotFoundError(f"{model}.svg not found in tmp")

  def removeSvg(model, rinkid):
    ''' also unused 
    '''
    if os.path.isfile(f'{PLOTDIR}/{rinkid}.svg'):
      os.unlink(f'{PLOTDIR}/{rinkid}.svg')
    if os.path.isfile(f'{WORKDIR}/{model}/{rinkid}.svg'):
      os.unlink(f'{WORKDIR}/{model}/{rinkid}.svg')
      return f'{rinkid} deleted ok' # success
    else: 
      raise FileNotFoundError(f'SVG not deleted {model}/{rinkid}')
'''
the
end
'''
