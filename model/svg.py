import matplotlib.pyplot as plt
import shapely.plotting
from shapely.geometry import Polygon

class Svg:

  VERBOSE    = False
  ADD_POINTS = False

  def draw(self, b1, svgfile):
    ''' plot a shapely box
    '''
    fig, ax = plt.subplots() 
    ax.set_aspect('equal')    # make x and y axis the same and set to CLEN
    plt.axis([0, (b1.BLOCKSZ[0] * b1.CLEN), 0, (b1.BLOCKSZ[1] * b1.CLEN)])

    for z in range(3): # bg 0 fg 1 top 2
      for pos in b1.cells:

        polygn = b1.polygon(pos, z)
        if polygn is None: continue
        if self.VERBOSE:
          print(f"{z} {pos} {polygn.geom_type} {b1.style.fill[pos]}")
        
        shapely.plotting.plot_polygon(
          polygn, ax=ax, add_points=self.ADD_POINTS,
          facecolor=b1.style.fill[pos][z],
          edgecolor=b1.style.stroke[pos][z], 
          linewidth=b1.style.stroke_width[pos][z], alpha=.5
        )

    t_class, t_name = self.fileName(svgfile)
    plt.title(f"{t_class} {t_name}")
    plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")

  def drawLine(self, block, svgfile):
    ''' preview a meandered plotfile
    '''
    fig, ax = plt.subplots() 
    width   = block.BLOCKSZ[0] * block.CLEN
    height  = block.BLOCKSZ[1] * block.CLEN
    ax.set_aspect('equal') # make x and y axis the same and set to CLEN
    plt.axis([0, width, 0, height])

    for pos in block.guide:
      for z, linestr in enumerate(block.guide[pos]):
        if self.VERBOSE: print(f'{pos=} {z=} {block.style.fill[pos]=}')
        shapely.plotting.plot_line(
          linestr, ax=ax, add_points=self.ADD_POINTS,
          color=block.style.fill[pos][z]
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

   def plotLine(self, line, fn, visible=True, title=True, width=.5):
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
     shapely.plotting.plot_polygon(
       box, ax=ax, add_points=True, 
       alpha=.5,
       facecolor='#CCC',
       edgecolor='#000',
       linewidth=1
     )
     plt.savefig(f"tmp/{t_class}_{t_name}.svg", format="svg")

'''
the
end
'''
