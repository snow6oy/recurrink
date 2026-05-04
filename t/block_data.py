import unittest
import pprint
from block.data import BlockData
from cell import Commit, Clone
from cell.minkscape_2 import minkscape_2

class Test(unittest.TestCase):
  ''' test_c and test_e create a fake entry
      clean the entry before re-test
      running `bash sql/t.sh` will do the cleaning
     
      all tests depend on this entry 
      run after mid:1 and ver:1 have been created

INSERT INTO rinks (rinkid, mid, ver)
VALUES ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',1,1);

remove from layers after test
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.bd     = BlockData()
    self.commit = Commit()
    self.clone  = Clone()
    self.ver    = 4 # stabilo68 new ver
    self.rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' # fake rink
    self.cellV2 = {
      'color': {
        'background': None,
              'fill': '#ccff00',
           'opacity': 1.0
      },
      'geom': {
              'name': 'circle',
              'size': 'medium',
            'facing': 'C',
               'top': False
      },
      'stroke': {
              'fill': '#ff00cc',
           'opacity': 0.5,
             'width': 1,
         'dasharray': 2
      }
    }
    self.cellV1 = {
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

  def test_a(self):
    # send empty list to avoid creating unwanted records
    colors = self.bd.colors(self.ver, colors=list())
    self.assertFalse(self.bd.count)

  def test_b(self):
    ''' does not include record created by test_c
DELETE FROM colors WHERE ver = 4 AND penam = 'zz';
    '''
    pen_count = self.bd.colorsRead(self.ver)
    self.assertEqual(30, len(pen_count))

  def test_c(self):
    ''' add one row to the colors table
        99 is not a valid version
        but colorsWrite ignores it anyway and forces new ver
    '''
    data = dict()
    data['#999999'] = 'zz'
    colors = self.bd.colorsWrite(data, self.ver)
    self.assertEqual(1, self.bd.count)

  def test_d(self):
    old_ver = 11
    new_ver = self.bd.version(old_ver)
    self.assertEqual(4, new_ver)

  def test_e(self):
    ''' create fake rink
        meta is based on data retrieved from db1

DELETE FROM rinks WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz';
    '''
    mid      = 1
    created  = None
    pubdate  = None 
    self.bd.rinksWrite(self.rinkid, mid, self.ver, 90, 0.4)
    self.assertTrue(self.bd.count)

  def test_f(self):
    ''' read rink created by test_e
    rink = self.bd.rinksRead(self.rinkid)
    '''
    rink = self.bd.rinks(self.rinkid)
    self.assertEqual(1, rink[0]) # zzz rink has model id: 1

  def test_g(self):
    ''' update rink to use new pen
    '''
    mid      = 1
    new_ver  = 6
    created  = None
    pubdate  = None 
    rinkdata = [mid, new_ver, 90, 0.4, created, pubdate]
    # None, None created published
    self.bd.rinks(self.rinkid, rinkdata)
    self.assertTrue(self.bd.count)

  def test_h(self):
    ''' get factor for rink
    '''
    rink  = self.bd.rinks(self.rinkid)
    self.assertTrue(0.5, rink[3])

  def test_i(self, label='a', fg=True, bg=False, top=False, expected=2):
    #print(f'{fg=} {bg=} {top=} {self.id()}')
    cell                                   = self.cellV2
    cell['geom']['top']                    = top
    if bg: cell['color']['background']     = '#00cc00',
    if top and not fg: cell['geom']['top'] = False # demote to layer 1

    celldata  = { label: cell }
    celldata  = self.commit.dataV2(celldata)
    self.bd.layersWrite(self.rinkid, celldata)
    self.assertEqual(expected, self.bd.count) # check rows were inserted

  def test_j(self): self.test_i(label='b', fg=True, bg=True, expected=2)
  def test_k(self): 
    self.test_i(label='c', fg=True, bg=True, top=True, expected=3)
  def test_l(self):
    self.test_i(label='d', fg=False, bg=True, top=True, expected=2)
  def test_m(self): self.test_i(label='e', fg=True, top=True, expected=3)

  def test_n(self):
    ''' read test cell from layers table
    '''
    expected = {
      'a': 2, 'b': 2, 'c': 3, 'd': 2, 'e': 3
    } 
    cells    = self.bd.layersRead(self.rinkid)
    #self.pp.pprint(cells)
    for label in ['a', 'b', 'c', 'd', 'e']:
      self.assertEqual(expected[label], len(cells[label]))
    
  def test_o(self):
    ''' test the transformer
    '''
    cell = self.cellV2
    #self.pp.pprint(cell)
    cell = self.commit.dataV2({'a': cell})
    self.assertFalse(len(cell['a'][0]))
    self.assertTrue(len(cell['a'][1]))

  def test_p(self):
    ''' transform Y3ML to DBV3
    '''
    v3 = self.commit.dataV3(minkscape_2.cells)
    #self.pp.pprint(v3)
    self.assertTrue(len(v3['a']))

  def test_q(self):
    ''' convert Y3ML to DBV2
    '''
    #self.pp.pprint(minkscape_2.cells)
    v3 = self.commit.dataV3(minkscape_2.cells)
    self.assertEqual(2, len(v3['a']))

  def test_r(self):
    ''' transform DBV3 to YAML for backward compatibility
  
        t.blockdata.Test.test_e creates zzz rink
        self.test_a creates layers
    '''
    cells = self.bd.layersRead(self.rinkid)
    yaml  = self.clone.databaseToYaml(cells['a'])
    # self.pp.pprint(yaml)
    a     = list(yaml.keys()) 
    [self.assertTrue(k in a) for k in ['geom', 'color', 'stroke']]

  def test_s(self):
    ''' update color
    '''
    cell_a  = self.bd.layersRead(self.rinkid)
    invert  = '#3300ff'
    # self.pp.pprint(cell_a)
    fg      = list(cell_a['a'][1])
    fg[3]   = invert
    cell_a['a'][1] = tuple(fg)
    self.bd.layers(self.rinkid, celldata=cell_a)
    self.assertTrue(self.bd.count)

    
'''
the 
end
'''
