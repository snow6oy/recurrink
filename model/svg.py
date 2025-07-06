import matplotlib.pyplot as plt
import shapely.plotting
from shapely.geometry import Polygon

class Svg:

  VERBOSE    = False
  ADD_POINTS = False

  def draw(self, b, svgfile):

    fig, ax = plt.subplots() 
    ax.set_aspect('equal')    # make x and y axis the same and set to CLEN
    plt.axis([0, (b.BLOCKSZ[0] * b.CLEN), 0, (b.BLOCKSZ[1] * b.CLEN)])

    # TODO refactor to use style for iteration ??
    for z in range(3): # bg 0 fg 1 top 2
      for pos, c in b.cells.items():

        if z == 2 and len(c.interiors) > 1: 
          lring = c.interiors[1]                   # top
        elif z == 2: continue 
        elif z == 1: lring = c.interiors[0]        # fg
        elif z == 0: lring = c.exterior            # bg

        if self.VERBOSE:
          print(f"0 {b.BLOCKSZ[0] * b.CLEN} 0 {b.BLOCKSZ[1] * b.CLEN}")
          print(f"{z} {pos} {len(c.interiors)} {b.style.fill[pos]}")
        
        shapely.plotting.plot_polygon(
          Polygon(lring), ax=ax, add_points=self.ADD_POINTS,
          facecolor=b.style.fill[pos][z],
          edgecolor=b.style.stroke[pos][z], 
          linewidth=b.style.stroke_width[pos][z]
        )

    t_class, t_name = self.fileName(svgfile)
    plt.title(f"{t_class} {t_name}")
    plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")
    '''
    svgfile = svgfile if svgfile else "tmp/not_bft.svg"
    plt.savefig(svgfile, format="svg")
    '''

  def drawLine(self, block, svgfile):
    ''' preview a plotfile
    '''
    fig, ax = plt.subplots() 
    width   = block.BLOCKSZ[0] * block.CLEN
    height  = block.BLOCKSZ[1] * block.CLEN
    ax.set_aspect('equal') # make x and y axis the same and set to CLEN
    plt.axis([0, width, 0, height])

    for pos in block.guide:
      for z, linestr in enumerate(block.guide[pos]):
        shapely.plotting.plot_line(
          linestr, ax=ax, add_points=self.ADD_POINTS,
          color=block.style.stroke[pos][z]
        )

    t_class, t_name = self.fileName(svgfile)
    plt.title(f"{t_class} {t_name}")
    plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")

  def fileName(self, fn):
    ''' hijack unittest to auto-gen file names

    example output of unittest self.id() is t.meander.Test.test_o
    '''
    tid = fn.split('.')  # unittest self.id()
    return tid[1], tid[3]


class SvgWriter(Svg):
   ''' for testers 
   '''

   def plotLine(self, line, fn, visible=True, title=True, width=1):
    ''' use shapely.plotting :)
    '''
    if line.geom_type not in ['LineString', 'LinearRing','MultiLineString']:
      raise ValueError(f'wrong geometry {line.geom_type}')
    fig, ax = plt.subplots()
    ax.axes.get_xaxis().set_visible(visible)
    ax.axes.get_yaxis().set_visible(visible)
    t_class, t_name = self.fileName(fn)
    if title: plt.title(f"{t_class} {t_name}")
    shapely.plotting.plot_line(line, ax=ax, linewidth=width, add_points=False)
    plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")

   def plot(self, box, fn, title=True):
     fig, ax = plt.subplots()
     t_class, t_name = self.fileName(fn)
     if title: plt.title(f"{t_class} {t_name}")
     shapely.plotting.plot_polygon(box, ax=ax, add_points=False)
     plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")


'''
the
end
'''

