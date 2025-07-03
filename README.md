# Adding support for plotters

SVGs have overlapping layers. 
When overlapping colours are used together a new, third colour emerges.
This is explained in >[the color theory of Don Cooke](https://www.stumptownprinters.com/news/2016/10/26/color-by-overprinting)<

Plotters are linear. Overlapping is done by drawing lines with different pens over the same surface.

Not BFT is a new version of recurrink that implements a Cell as a Shapely Polygon. A major problem to resolve in the new version is how to transform 
existing rinks to 

1. Plot lines that can represent two-dimensional shapes - how to fill?
1. Overlap colours cleanly

### Meander 
Meander and Spiral can fill certain, angular shapes. Circles and Triangles are not included.

### Flatten
Flatten attempts to collapse a multi-layered cell onto a two-dimensional plane.
Separating the cells gives cleaner results when plotted, but there are many unresolved edge cases. 

### Solutions

#### 1. Toggle Flatten by position

Flatten is both global and dynamic. Global because ALL positions on the block are flattened whenever the output is set to a plotter. The new shapes defined by Flatten are dynamically written to SVG.

This solution converts flatten into a toggle feature. This can be useful when flatten encounters an edge case that causes the build to fail.

For example
```
  positions = {
    (0, 0): ('a', 'c', True),  # c is both cell and top
    (1, 0): ('b', 'd', True),  # d is only top
    (2, 0): ('c', None, False)
  }
```
In this example, c will overlay a in the first position. In the final position, however, c should be flattened against the lower background cell. 

#### 2. Clone and modify
In the event that colours clash when overlapped and there are build issues caused by Flatten, then rink can be cloned and the new flatten shapes used to replace the originals. These are: Gnomon, Parabola and Square Ring.

The new shapes provide a manual alternative to flatten. Dirty overlaps are removed by reducing the surface area of adjacent shapes. For example, by swapping a square for a parabola

#### 3. Flatten to YAML
YAML is a nice to have for authoring. 
Replacing the init CSV with an init YAML will be easier for the author.

This option combines both of the previous solutions. 
It involves writing the new shape definitions to a static YAML.
Then manual corrections to the YAML can override the automated definitions. It requires the codebase to support the new shapes Gnomon/Parabola/SquareRing. 

To process a flattened YAML will however, present some new problems. 
The current data model is based on three-layers.
Each shape is positioned relative to x,y with z defining the layer.
After flattening, z is irrelevant, but there are more positions on the 2-d plane.

```
+----+---+----+
| NW | N | NE |
+----+---+----+
|  W | C | E  |
+----+---+----+
| SW | S | SE |
+----+---+----+
```
Consider the following entry in the CSV file
```
shape: square, size: small, facing: all
```
This will currently produce a shape at position __C__ (c = centre).
Flattening can produce shapes for any of the nine positions in the above table.

> How to extend the YAML nomenclature to describe these new outcomes?

Perhaps the `facing` key can accept two value sets:
1. north, south, east, west that are positioned relative to bottom left
2. NW .. SE that are positioned relative to the nine shown above


### Data Model
TODO evolve the data model
1. to explain how the code is packaged
2. to extend the model to support flattening

```
gavin@macarol:~/code/recurrink$ find cell block model -name "*.py"

cell.data
cell.layer
cell.shape.rectangle
cell.shape.gnomon

block.styles
block.meander
block.tmpfile
block.make
block.data

model.svg
model.db
model.data

```
Three tables in Cell
- cells c.ext int0 int1
- style [0-2]
- direction [0-2]


### TODO
- add new flatten shapes to codebase
- ~Gnomon should support sizes: small and medium~
- add Inkscape palettes
- validation should be done by Shape
- CLEN is always 6 !
- implement new YAML by extending TmpFile
- add flatten to not bft
- mock toggle using code and run cflat tests
- resolve flatten errors by using Don Cooke theory and check results
- produce a YAML from Flatten and stop toggling
- ~titles for matplotlib~
- ~run cflat test suite~
- ~on dev branch install scripts/not_bft.py as ./recurrink~
- ~add meander for rectangle~
- ~'all' from guide calls Spiral not Meander~

Matplot SVG has limitations
- stroke is ignored, sent as edgecolour ???
- group order is ignored e.g. koto has 2 invisible squares in box view

New YAML should also remove support for small lines (use square instead)

Using kwargs send set_alpha based on fill_opacity
[](https://matplotlib.org/devdocs/api/_as_gen/matplotlib.artist.Artist.set_alpha.html#matplotlib.artist.Artist.set_alpha)




