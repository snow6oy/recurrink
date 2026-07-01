''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import pprint
from block import Build as BlockBuild
from .data import ModelData
from .svg import SvgModel
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Build(ModelData):
  ''' build or explode

      assumptions: gridsize is A3 (297 x 420 mm) 
      image is square: with margins grid approximate 270 x 270
      numbers of cells defined by cell length which prefers to be divisible by 3
      to ensure whole numbers: clen should be: 9 18 27 36 45 54 90 ..
  '''
  pp      = pprint.PrettyPrinter(indent=2)
  bb      = BlockBuild()

  def build(
    self, model, size, factor, explode=False, linear=False, layer=3, pgsize='A3L'
  ):
    pens      = self.pens()
    mid       = self.model(name=model)
    positions = self.blocks(mid)

    block, penam = self.bb.build(
      model, size, factor, 
      explode   = explode,
      linear    = linear,
      layer     = layer,
      mid       = mid,
      positions = positions,
      pens      = pens
    )

    if explode:
      svglin  = SvgModel(size, factor, ps=pgsize)
      svglin.explode(block)
      svgfile = model
    else:
      svglin   = SvgModel(size, factor)
      svglin.build(block)
      svgfile  = model
      svgfile += '_draw' if linear else '_paint'

    svglin.render(svgfile, linear)  # bool(args.line)
    return f'tmp/{svgfile}.svg was made with {penam}'

'''
the
end
'''
