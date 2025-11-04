# Model

A model is a collection of blocks. The module handles outputs to SVG.

SVG generation uses Etree except for tests which use matplotlib.

## Runbook
Recipes for reference

> as a plotter i want smooth pen strokes

check that antialiasing is enabled in Inkscape

### Config
> as a new installer i want to change config.py to suit my environment
```
from config import * 
```
including this will call Db.__init__() and expose directory[path]

> as a tester i want a sample rink 
```
from cell.minkscape import *
```
access data as minkscape.cells and minkscape.positions

> as a designer i want to experiment by plotting a test block 

## Design
things to do

### Sesanta
- 60mm is small to plot on A3
- move sesanta to model/sesanta and refactor to Block/Cell/Model
- support Linear.grid data model for custom SVG work
- experiment with SVG points: small polygons/circles or short polylines ?

### Bring back the scale parameter!
The rectangle will plot as 45x45 mm. 
Meanders with a 1mm gap will also scale down to half the size.
How?
```
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 180" width="270mm" height="90mm">
  <rect x="90" y="0" width="90" height="90" />
</svg>
```
The viewbox has maxX and maxY values that are double that of the viewport.
The viewport is defined by the width and height. 
- 2 * 270 = 540
- 2 *  90 = 180

This makes the rectangle appear half size. 
Building RINKs with a scale of .5 implies that 3 more rectangles are needed to fill the space.

### Combinations of Cell length, Size and Scale
These give nice whole numbers.
For example, with a size of 40 and a scale of 0.4 the cell len will be 16.
```
len  siz  scale
---------------
24 / 60 = 0.4
12 / 30 = 0.4

18 / 36 = 0.5
12 / 24 = 0.5
 9 / 18 = 0.5
```

### Publish and Build
+ reith broke because it uses old recurrink
- abort delete when pubdate is not null
- recurrink commit --mm should mv tmp/MODEL_mm.svg to rinks/MODEL/mm/abc123.svg

### The Great Regression
- split tests into (a) visual (b) logical
- build a model of rinks every week. Log errors 

### Scale 
- use transform() in SVG and move scale logic to model.Layout to runs as Export
- inkscape --export-type=png --export-width=1080 --export-height=1080 
  avoid the need to manually scale? Instead set transform(0.75) in SVG doc

- update recurringart.com/ make it fit for purpose
- list --attributes to show what can be added to /tmp/MODEL.txt, colour shapes

### Models and Compass
- migrate random generation into Compass (to keep data access clean)
- Support dynamic models e.g. read positions in YAML, commit changes 
- Evolve Compass so that it can dynamically generate a model based on rules
  Symmetry, palette, divisbility, distribution (balance of intense versus space)
- grep dump and make MODEL.sql
- new model: large square + four diamonds with transparencies 
- new shape: diagonl / \ a 90 degree triangle
- add new models inspired by recurrenceModelNames.pdf
- add the spiral, envelopes and morocco models
- migrate rinks in /recurrencesArchive to postgres

### Data model
an entity diagram of the DB 1..n

![](../tutorial/dbentity.svg)

## Release notes
_ argparse allows any cell length but warns if indivisible by 9
_ build has stopped using matplot lib because
_ SvgLinear became SvgModel and SvgWriter moved to tester.py
