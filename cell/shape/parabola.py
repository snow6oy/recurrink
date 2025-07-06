class Parabola:
  ''' u-shaped parallelograms
      north n south u ... 
  '''
  VERBOSE = False
  def __init__(self):
    self.name = 'parabola'

  def coords(self, dim, kwargs):
    ''' define the input so Shapely Polygon can create a U shape
    '''
    X, Y, W, H, a, b, c, d, *A = dim

    facing    = kwargs['facing']
    direction = {
      'north': [(X,Y),(X,H),(W,H),(W,Y),(c,Y),(c,d),(a,d),(a,Y)],
      'south': [(X,Y),(X,H),(a,H),(a,b),(c,b),(c,H),(W,H),(W,Y)],
       'west': [(X,Y),(X,H),(W,H),(W,d),(a,d),(a,b),(W,b),(W,Y)],
       'east': [(X,Y),(X,b),(c,b),(c,d),(X,d),(X,H),(W,H),(W,Y)]
    }
    return direction[facing]

  def guide(self, facing):
    ''' translate facing into another facing that gnomon and edge
        will convert into the guide used by Meander
    '''
    control = {
      'north': ['NE', 'west'],
      'south': ['SW', 'east'],
       'east': ['SE', 'north'],
       'west': ['NW', 'south']
    }
    if facing in control:
      control[facing].insert(0, 'composite')
      return tuple(control[facing])
    else: raise KeyError(f'all at sea > {facing} < without control')

'''
the
end
'''
