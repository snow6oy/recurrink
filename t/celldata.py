import unittest
import pprint
from cell import CellData
from cell.minkscape_2 import minkscape_2

# TODO merge with t.geometry
class Test(unittest.TestCase):
  ''' tests depend on this entry 
      run after mid:1 and ver:1 have been created

INSERT INTO rinks (rinkid, mid, ver)
VALUES ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',1,1);

remove from layers after test
  '''

  def setUp(self):
    self.pp     = pprint.PrettyPrinter(indent=2)
    self.cd     = CellData()
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
    self.cell = {
                'bg': None,
             'shape': 'circle',
              'size': 'medium',
            'facing': 'C',
               'top': False,
              'fill': '#ccff00',
      'fill_opacity': 1.0,
            'stroke': '#ff00cc',
    'stroke_opacity': 0.5,
      'stroke_width': 1,
  'stroke_dasharray': 2
    }

  def test_a(self, label='a', fg=True, bg=False, top=False, expected=2):
    #print(f'{fg=} {bg=} {top=} {self.id()}')
    cell = self.cell
    cell['top'] = top
    if bg: cell['bg'] = '#00cc00',
    if top and not fg: cell['top'] = False # demote to layer 1

    celldata  = { label: cell }
    celldata  = self.cd.dataV1(celldata)
    self.cd.layersWrite(self.rinkid, celldata)
    self.assertEqual(expected, self.cd.count) # check rows were inserted

  def test_b(self): self.test_a(label='b', fg=True, bg=True, expected=2)
  def test_c(self): 
    self.test_a(label='c', fg=True, bg=True, top=True, expected=3)
  def test_d(self):
    self.test_a(label='d', fg=False, bg=True, top=True, expected=2)
  def test_e(self): self.test_a(label='e', fg=True, top=True, expected=3)

  def test_f(self):
    ''' read test cell from layers table
    '''
    expected = {
      'a': 2, 'b': 2, 'c': 3, 'd': 2, 'e': 3
    } 
    cells    = self.cd.layersRead(self.rinkid)
    #self.pp.pprint(cells)
    for label in ['a', 'b', 'c', 'd', 'e']:
      self.assertEqual(expected[label], len(cells[label]))
    
  def test_g(self):
    ''' test the transformer
    '''
    cell = self.cell
    #self.pp.pprint(cell)
    cell = self.cd.dataV1({'a': cell})
    self.assertFalse(len(cell['a'][0]))
    self.assertTrue(len(cell['a'][1]))

  def test_h(self):
    ''' transform Y3ML to DBV3
    '''
    v3 = self.cd.dataV3(minkscape_2.cells)
    #self.pp.pprint(v3)
    self.assertTrue(len(v3['a']))

  def test_i(self):
    ''' convert Y3ML to DBV2
    '''
    #self.pp.pprint(minkscape_2.cells)
    v3 = self.cd.dataV3(minkscape_2.cells)
    self.assertEqual(2, len(v3['a']))

  def test_j(self):
    ''' transform DBV3 to YAML for backward compatibility
  
        t.blockdata.Test.test_e creates zzz rink
        self.test_a creates layers
    '''
    cells = self.cd.layersRead(self.rinkid)
    yaml  = self.cd.txDbv3Yaml(cells)
    a     = list(yaml['a'].keys()) 
    ''' self.pp.pprint(a)
    '''
    [self.assertTrue(k in a) for k in ['geom', 'color', 'stroke']]

  def test_k(self):
    ''' update color
    '''
    cell_a  = self.cd.layersRead(self.rinkid)
    invert  = '#3300ff'
    # self.pp.pprint(cell_a)
    fg      = list(cell_a['a'][1])
    fg[3]   = invert
    cell_a['a'][1] = tuple(fg)
    self.cd.layers(self.rinkid, celldata=cell_a)
    self.assertTrue(self.cd.count)

    
'''
the 
end
'''
