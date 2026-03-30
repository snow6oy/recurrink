''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import pprint
from model import ModelData, SvgModel
from block import TmpFile, BlockData, Make
from cell import InputValidator
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Build:
  ''' build or explode

      assumptions: gridsize is A3 (297 x 420 mm) 
      image is square: with margins grid approximate 270 x 270
      numbers of cells defined by cell length which prefers to be divisible by 3
      to ensure whole numbers: clen should be: 9 18 27 36 45 54 90 ..
  '''
  pp      = pprint.PrettyPrinter(indent=2)
  tf      = TmpFile()
  md      = ModelData()
  bd      = BlockData()

  def build(self, model, size, factor, explode=False, linear=False, layer=3):
    svglin    = SvgModel(size, factor)
    metadata  = self.tf.readConf(model, meta=True)    
    celldata  = self.tf.readConf(model)
    pens      = self.md.pens()
    ver       = pens.index(metadata['palette'])
    mid       = self.md.model(name=model)
    positions = self.md.blocks(mid)
    colors    = self.bd.colors(ver)
    celldata  = self.tf.readConf(model)
    penam     = dict()              # convert to dict for svg render
    for k, v in colors: penam[k] = v
    block     = Make(size, linear, pen_names=penam)
    block.walk(positions, celldata, z=layer)
    block.hydrateGrid()

    if explode:
      svglin.explode(block)
      svgfile = model
    else:
      uniq        = list(penam.keys())
      iv          = InputValidator(ver=ver)
      iv.uniqfill = uniq
      [iv.validate(label, cell) for label, cell in celldata.items()]
      svglin.build(block)
      svgfile  = model
      svgfile += '_draw' if linear else '_paint'

    svglin.render(svgfile, linear)  # bool(args.line)
    return f'tmp/{svgfile}.svg was made with {metadata["palette"]}'

'''
the
end
'''
