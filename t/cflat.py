import unittest
import pprint
from pathlib import Path
from block import TmpFile, Make, BlockData, Views
from model import ModelData, SvgLinear
from cell.minkscape import *

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.models = {
      'minkscape': None,
      'buleria': '7e731bfc1863c186616d2b3de09a9b6b',
      'koto': '4be0d482b6a2806857b017bf3c5047aa',
      'sonny': '47698c060ba647fee5bebc3548644b88',
      'waltz': 'e2703e9ea6733f9c47458bcf5afb8b45',
      'eflat': '3409bc82f3b0bfa90fb29fd23cb51abc',
      'bossa': '045ffc5caa76af20a1bbf9783aeb196c',
      'afroclave': '6b3779708184e346d31c0c3a6de3d885',
      'pitch': 'f049e4fe093d87f09e57e259334bc6e2',
      'mambo': 'b6b1998b57aa1c31e5c4ff6e74fd5a58'
    }
    # triangles yuck a2397e60976e01cba87a1e9e5467df2d

  def test_a(self, model=None, line=False):
    block = Make(clen=90, linear=line) # default to clen: 9
    svg   = SvgLinear(clen=90)
    view  = Views()
    tf    = TmpFile()

    if model: 
      digest = self.models[model]
      clone  = Path(f'clone/{model}.yaml')

      if not clone.is_file():
        print(f'cloning {digest}')
        _, _, _, ver = view.readMeta(digest=digest)
        celldata     = view.read(digest=digest)
        tf.setVersion(ver)
        tf.write(model, celldata)

      b         = BlockData(model)
      positions = b.readPositions(model)
      cells     = tf.readConf(model)
      block.walk(positions, cells)
    else:     
      model = 'minkscape'
      cells = tf.readConf(model)
      block.walk(minkscape.positions, cells)

    svgfile = f'{model}_line' if line else f'{model}_box'
    block.hydrateGrid()
    svg.build(block)
    svg.render(svgfile, line=line)

  def test_b(self): self.test_a(line=True)
  def test_c(self): self.test_a(model='buleria')
  def test_d(self): self.test_a(model='buleria', line=True)
  def test_e(self): self.test_a(model='koto')
  def test_f(self): self.test_a(model='koto', line=True)
  def test_g(self): self.test_a(model='sonny')
  def test_h(self): self.test_a(model='sonny', line=True)
  def test_i(self): self.test_a(model='eflat')
  def test_j(self): self.test_a(model='eflat', line=True)
  def test_k(self): self.test_a(model='waltz')
  def test_l(self): self.test_a(model='waltz', line=True)
  def test_m(self): self.test_a(model='bossa')
  def test_n(self): self.test_a(model='bossa', line=True)
  def test_o(self): self.test_a(model='afroclave')
  def test_p(self): self.test_a(model='afroclave', line=True)
  def test_q(self): self.test_a(model='pitch')
  def test_r(self): self.test_a(model='pitch', line=True)
  def test_s(self): self.test_a(model='mambo')
  def test_t(self): self.test_a(model='mambo', line=True)

'''
= Test Cases
RESULTS
	 	Wirefm	Block1	Blocks
8 buleria 	y	y	y
7 koto		y	y	y	square overlaps spiral
6 sonny		y	y	y
5 eflat		y	y	y	ignore multi
4 waltz		y	N	-	meander uneven points
3 bossa  	y	y	y	square overlaps spiral
2 afroclave	y	y	y	ignore multi
1 pitch		y	N	-	meander unevan points
0 mambo		y	y	y	ignore multi

IRREGULAR
e444ac14353eca218fdf209b2578b498 12pt Polygon
734e59c584edf1d2db1e42a075772d12 uneven Gnomon
5bb9fc857e9b0a9520a9903f4c9a7e55 spade

FAIL wireframe
045ffc5caa76af20a1bbf9783aeb196c bossa human MULTI-PART GEOM NOT IMPL

DONE wireframe
eed35becd75091341b6da3199b93a3ec funkytrunk human
e5bbfedf1e82e99b20a6f23d44107820 marchingband human
8a481181d5fb3df6119edb2cfcff4858 spiral machine
2eab595a7b825a44858b8ec3e861286d tumbao human
f74c82f8d889e9ecbd1b76eb8f4b370f fourfour human
fd6476d46ea4a49bc7f2b1d6d1c0e57c timpani machine
d2d0f3b7418aa6c33c3d23c63874f599 waltz machine
7a2552cb2e0e03e62e45fd9332e6c572 syncopated machine
899b4ea0734bdf771476b14b8c934f1a arpeggio human
a2397e60976e01cba87a1e9e5467df2d bossa human
3cc0083b44db3d7714311565422f4c7b tumbao human
'''

'''
the
end
'''
