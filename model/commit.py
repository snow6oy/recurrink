import os
import datetime 
import pprint
from model import ModelData
from block import PaletteMaker, TmpFile, BlockData
from cell import CellData
from config import *
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Commit:
  ''' read config, write to database and return digest
      clean file system except for tmp/model.txt

    When both pal and digest are given remember to do this first
      export view using recurrink init -v --> /tmp/MODEL.txt
      export pal from using palette init -p

    When only pal then
      convert palette in tmpfile to sql INSERT but first manually 
      create tmpfile NEW_PAL.txt 
      add NEW_PAL to friendly_name
      use the index of config.friendly_name[] as arg

    rinkid: 180f1989f54ff03291ec31e164f2a79f
  '''
  pp      = pprint.PrettyPrinter(indent=2)
  pmk     = PaletteMaker()
  tf      = TmpFile()
  md      = ModelData()
  bd      = BlockData()
  cd      = CellData()
  WORKDIR = config.directory['rinks']
  PUBDIR  = config.directory['pubq']
  PALDIR  = config.directory['palettes']
  fnam    = md.pens()  # pal.friendlyPenNames()

  def _palswap(self, palver, rinkid): 
    ''' another way would be for clone to transform the rink to new pal
      then commit would read rinkid from YAML and update
    '''
    celldata  = cd.layers(rinkid)  #view.read(digest=dig) 
    ver       = bd.version(palver) 
    oc        = tf.getOldColors(rinkid)
    #pp.pprint(oc)
    colors    = bd.colors(palver)
    #pp.pprint(colors)
    uniqfill  = set([c[0] for c in colors])  # strip out penam
    #pp.pprint(uniqfill)
    nc        = pmk.setLookUp(uniqfill) # for search the new colour
    swp       = pmk.swapColors(oc, nc)
    for label, cell in celldata.items():
      layers = list()
      for z in cell:
        old_stroke   = z[3]
        new_layer    = list(z)
        new_layer[3] = swp[old_stroke]
        layers.append(tuple(new_layer))
      celldata[label] = layers  # update db colors 
    #pp.pprint(celldata)
    rinkdata    = list(bd.rinks(rinkid))
    rinkdata[2] = ver
    bd.rinks(rinkid, rinkdata)
    out  = f'new ver {rinkdata[3]} updated {bd.count=}'
    cd.layers(rinkid, celldata)
    out += f'cell updates {cd.count=}'
    return out

  def addColor(self, penam):
    ''' create new color entries as bd.colours(ver, colors=list())
        entry in pens table should be made manually before
    '''
    gpldata = self.pmk.readInkscapePal(self.PALDIR, f'{penam}.gpl')
    pens    = self.md.pens()
    if penam in pens:
      #self.pp.pprint(gpldata)
      ver = pens.index(penam)
      self.bd.colors(ver, colors=gpldata)
      return f'{self.bd.count} colors added'
    else:
      return f'{penam} does not exist. add to pens table and try again'

  def addRink(self, model, size, factor):
    mid      = self.md.model(name=model)
    pens     = self.md.pens()
    celldata = self.tf.readConf(model)
    metadata = self.tf.readConf(model, meta=True)
    if metadata['palette'] in pens:
      ver = pens.index(metadata['palette'])
    else:
      ver = 0
    rinkid = self.tf.setDigest(celldata=celldata)
    response = f''' 
{rinkid}
{model} {mid=}
{metadata['palette']} {ver=}
{size=} {factor=}'''
    if os.path.isdir(f"{self.WORKDIR}/{model}"):
      self.bd.rinks(self.tf.digest, [mid, ver, size, factor])
      if self.bd.count:
        celldata = self.cd.dataV2(celldata)  # TODO should use dataV3 ?
        self.cd.layers(self.tf.digest, celldata=celldata)
          # response += self.moveTmpfile(model, self.tf.digest)
        response += ' ok'
      else:
        response += 'db error adding rink'
    else:
      raise FileNotFoundError(f"{model} not found in {self.WORKDIR}")
    return response

  def updateVer(self, penam, rinkid):
    ''' taking new ver from conf transformed by clone
    '''
    pens = self.md.pens()
    ver = pens.index(penam)
    mid, _, size, factor, created, pubdate = self.bd.rinks(rinkid)
    self.bd.rinks(rinkid, [mid, ver, size, factor, created, pubdate])
    return f'''
new palette: {penam}
rows impacted: {self.bd.count}'''

  def updatePubdate(self, rinkid): 
    # TODO rinksUpdate has to accept pubdate as well as ver
    ''' was used by reith but now it represents plotdate
        e.g. 2024-01-27 22:26:12
    '''
    rinkdata = self.bd.rinks(rinkid)
    if len(rinkdata) == 6:
      mid, ver, size, factor, created, pubdate = rinkdata
      pubdate = '{d:%Y-%m-%d %H:%M:%S}'.format(d=datetime.datetime.now())
      self.bd.rinks(rinkid, [mid, ver, size, factor, created, pubdate])
      out = f'''
pubdate: {pubdate}
rows impacted: {self.bd.count}'''
    else:
      out = f'{rinkid} not returned by db'
    return out

  def remove(self, rinkid):
    ''' remove is tricky because of db deps
    '''
    rinkdata = self.bd.rinks(rinkid) 
    if len(rinkdata):
      out   = self.bd.rinksDelete(rinkid)
      #model = self.md.model(mid=rinkdata[1])
      #out  += self.removeSvg(model, rinkid)
    else: 
      raise ValueError(f'nothing named {rinkid} in database')
    return out

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
