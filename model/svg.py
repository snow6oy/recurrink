import matplotlib.pyplot as plt
import shapely.plotting
from shapely.geometry import Polygon
class Svg:

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
