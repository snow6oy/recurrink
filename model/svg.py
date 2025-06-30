import matplotlib.pyplot as plt
import shapely.plotting

class Svg:

  VERBOSE    = False
  ADD_POINTS = False

  def draw(self, b):

    fig, ax = plt.subplots() 
    ax.set_aspect('equal')    # make x and y axis the same and set to CLEN
    print(f"0 {b.BLOCKSZ[0] * b.CLEN} 0 {b.BLOCKSZ[1] * b.CLEN}")
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
          print(f"{z} {pos} {len(c.interiors)} {b.style.fill[pos]}")
        
        shapely.plotting.plot_polygon(
          Polygon(lring), ax=ax, add_points=self.ADD_POINTS,
          facecolor=b.style.fill[pos][z],
          edgecolor=b.style.stroke[pos][z], 
          linewidth=b.style.stroke_width[pos][z]
        )
    plt.savefig(f"tmp/not_bft.svg", format="svg")

  def drawLine(self, block):
    ''' preview a plotfile
    '''
    fig, ax = plt.subplots() 

    for pos in block.guide:
      for z, linestr in enumerate(block.guide[pos]):
        shapely.plotting.plot_line(
          linestr, ax=ax, 
          color=block.style.stroke[pos][z]
        )
    plt.savefig(f"tmp/not_bft_line.svg", format="svg")

'''
the
end
'''
