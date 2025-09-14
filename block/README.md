# Block

A Block is a collection of cells. The block module provides operations on the collection.

## TODO
### Palette

- single-source-of-truth for palettes, see config.py in model/README
- Stencil broke recurrink commit because it counted colours

### Meander

- padding can be exposed to the interface, as meta in the conf?
- meander: concentric could work for circles, triangles and diamonds
- resurrect the original meander and apply N or E in conf 
- add meander.style as a YAML attribute


## Runbook
### Create a new palette with pen names

> as a plotter controller i want to see a  
> display of pen names in inkscape   
> so that i know which pen to load next  


Create a GPL file.
stabilo68.gpl example

```
cd Library/Application Support/org.inkscape.Inkscape/config/inkscape/palettes/

r   g   b      penam hex
---------------------------
128 255 179 #  13    80ffb3
```
From the GPLFILE generate a palette text file with permutations of fg:op:bg.

```
./recurrink init --inkpal GPLFILE

palettes/stabilo68.txt
```
The palette file is a tab-separated list
```
fill    opacity background
#d7e3f4 0.5     #483737
```
The hex in the GPL and ver will become a composite PRIMARY KEY in the pens table.

There is no method to create an entry in the inkpal table. 
To do it manually

```
INSERT INTO inkpal (ver, gplfile) VALUES (DEFAULT, 'sharpie');
```
Now import the values from the GPLFILE.

```
./recurrink commit --inkpal GPLFILE
```
Now palettes/GPLFILE is in sync with db.pens. 
Add the new pens to the palette table.

```
./recurrink commit -p12
11 new colours 
66 new entries
```
To see the pen names in Inkscape use explode.
Explode will pass them to the SVG.

1. Block.styles recieves pen names from db
1. Model.linear replaces group id with penam OR fallback to fill name

### Restore GPL file 

> as somone setting up a new machine i want to restore GPL files from database
To restore GPL files from DB for pals 8..11 

```
python -m scripts.mkgplfile
```

## Design

### Empty background
> as a rink designer i want the plotter to ignore the background layer

In the YAML set Background: ~

### Palette validation
> as a rink designer i want  
> to improve colour validation  
> with a simpler method of applying colour

relax validation so that at build time
fg:bg:op are checked individually, not as a trio
warn when opacity is a value other than (1, 0.5, 0)

checks are done against pens table
the colours table can be dropped
the method of generating a pallete with math.comb can be archived
the HTML palette pages show each colour exactly once (not trios)

cells table still refers to pid:sid
but they must honour existing pids. pid=fg:bg:op
at commit time, missing palette entries with valid values 
but a unique combination  should be silently added 
e.g. FF0000 0.1 00FF00  
ver can be dropped from palette table
this may cause PIDs with duplicate fg:op:bg combinationns?

### Palette conversion
> as a plotter i want convert all rinks to use pen palettes

Build a rink with `./recurrink build -vRINKID`  
Then run python `-m scripts.palswap RINKID VER`  
This will find-nearest colour and build  
`tmp/MODEL_PALSWAP.svg`  
The new and old rinks are compared visually.  
Other palettes can be tried. Once ready.  
`python -m scripts.palswap MODEL ` 
will swap PIDs in the database.  

#### Find nearest colour
```
rgb1 is a list of FG:BG from old pal
rgb2 is from new pal

DISTANCE = 255 * 3
distance = r1 - r2 + g1 - g2 + b1 - b2
if distance < DISTANCE:
  closest[rgb1] = rgb2
  DISTANCE = distance
```
